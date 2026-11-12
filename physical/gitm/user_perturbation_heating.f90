subroutine user_perturbation

  ! Abstract, synthetic localized heat source for a non-operational sensitivity
  ! study (thermosphere-debris-selective-decay, physical-model rebuild).
  !
  ! q(x,t) = P(t) * w(x) / sum_cells( w * CellVolume )        [W m^-3]
  ! w(x)   = exp(-d_h^2 / (2 sigma_h^2)) * exp(-(z - z0)^2 / (2 sigma_z^2))
  ! P(t)   = P0 * cosine-tapered boxcar over [t_on, t_on + duration]
  !
  ! d_h is the great-circle distance at radius (R_E + z0). The discrete
  ! normalisation makes the deposited power equal P(t) on the model grid at
  ! every step, independent of resolution. The heating enters the neutral
  ! energy equation through GITM's UserHeatingRate term (normalised
  ! temperature increment per step): dT_norm = Dt * q / (rho * cp * TempUnit).
  !
  ! Parameters are read from UA/DataIn/user_heating.in:
  !   P0_W lat0_deg lon0_deg z0_km sigma_h_km sigma_z_km t_on_s duration_s ramp_s
  ! P0_W <= 0 disables the source (paired control run).

  use ModGITM
  use ModInputs
  use ModConstants
  use ModTime
  use ModMpi
  use ModSources, only: UserHeatingRate
  use ModKind, only: Real8_

  implicit none

  logical, save :: IsInit = .false.
  real, save :: P0, Lat0, Lon0, Z0, SigH, SigZ, TOn, TDur, TRamp
  real(Real8_), save :: ECum = 0.0
  real, save :: TLastLog = -1.0e32

  integer :: iBlock, iLon, iLat, iAlt, iError, iUnit
  real :: w(nLons, nLats, nAlts, nBlocks)
  real :: Local(2), Global(2), x, Pt, rr, cosd, dh, dz
  real :: sLat0, cLat0

  UserHeatingRate = 0.0

  if (.not. IsInit) then
    iUnit = 87
    open(iUnit, file='UA/DataIn/user_heating.in', status='old')
    read(iUnit, *) P0, Lat0, Lon0, Z0, SigH, SigZ, TOn, TDur, TRamp
    close(iUnit)
    IsInit = .true.
    if (iProc == 0) then
      write(*, *) 'user_heating: P0,lat0,lon0,z0,sigh,sigz,ton,tdur,tramp = ', &
        P0, Lat0, Lon0, Z0, SigH, SigZ, TOn, TDur, TRamp
      open(iUnit, file='UA/data/user_heating_log.dat', status='replace')
      write(iUnit, '(a)') '# t_since_start_s  P_target_W  P_deposited_W  E_cum_J  Dt_s'
      close(iUnit)
    endif
  endif

  x = real(CurrentTime - StartTime) - TOn
  Pt = 0.0
  if (P0 > 0.0 .and. x >= 0.0 .and. x <= TDur) then
    Pt = P0
    if (TRamp > 0.0) then
      if (x < TRamp) Pt = P0*0.5*(1.0 - cos(pi*x/TRamp))
      if (x > TDur - TRamp) Pt = P0*0.5*(1.0 - cos(pi*(TDur - x)/TRamp))
    endif
  endif

  Local = 0.0
  if (Pt > 0.0) then
    sLat0 = sin(Lat0*pi/180.0)
    cLat0 = cos(Lat0*pi/180.0)
    rr = (R_Earth + Z0*1000.0)
    do iBlock = 1, nBlocks
      do iAlt = 1, nAlts
        do iLat = 1, nLats
          do iLon = 1, nLons
            cosd = sLat0*sin(Latitude(iLat, iBlock)) + &
                   cLat0*cos(Latitude(iLat, iBlock))* &
                   cos(Longitude(iLon, iBlock) - Lon0*pi/180.0)
            cosd = max(-1.0, min(1.0, cosd))
            dh = rr*acos(cosd)
            dz = Altitude_GB(iLon, iLat, iAlt, iBlock) - Z0*1000.0
            w(iLon, iLat, iAlt, iBlock) = &
              exp(-dh**2/(2.0*(SigH*1000.0)**2))*exp(-dz**2/(2.0*(SigZ*1000.0)**2))
            Local(1) = Local(1) + w(iLon, iLat, iAlt, iBlock)* &
                       CellVolume(iLon, iLat, iAlt, iBlock)
          enddo
        enddo
      enddo
    enddo
    call MPI_AllREDUCE(Local, Global, 2, MPI_REAL, MPI_SUM, iCommGITM, iError)
    Local = 0.0
    if (Global(1) > 0.0) then
      do iBlock = 1, nBlocks
        do iAlt = 1, nAlts
          do iLat = 1, nLats
            do iLon = 1, nLons
              ! q [W m^-3] -> normalised temperature increment over Dt
              UserHeatingRate(iLon, iLat, iAlt, iBlock) = &
                Dt*Pt*w(iLon, iLat, iAlt, iBlock)/Global(1)/ &
                (Rho(iLon, iLat, iAlt, iBlock)*cp(iLon, iLat, iAlt, iBlock)* &
                 TempUnit(iLon, iLat, iAlt))
              ! back-computed deposited power (diagnostic)
              Local(2) = Local(2) + UserHeatingRate(iLon, iLat, iAlt, iBlock)* &
                         Rho(iLon, iLat, iAlt, iBlock)*cp(iLon, iLat, iAlt, iBlock)* &
                         TempUnit(iLon, iLat, iAlt)* &
                         CellVolume(iLon, iLat, iAlt, iBlock)/Dt
            enddo
          enddo
        enddo
      enddo
    endif
  endif

  call MPI_AllREDUCE(Local, Global, 2, MPI_REAL, MPI_SUM, iCommGITM, iError)
  ECum = ECum + Global(2)*Dt

  if (iProc == 0 .and. P0 > 0.0 .and. &
      (real(CurrentTime - StartTime) - TLastLog >= 10.0 .or. Pt > 0.0)) then
    TLastLog = real(CurrentTime - StartTime)
    open(87, file='UA/data/user_heating_log.dat', status='old', position='append')
    write(87, '(5es16.8)') real(CurrentTime - StartTime), Pt, Global(2), real(ECum), Dt
    close(87)
  endif

end subroutine user_perturbation
