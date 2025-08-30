Name:           How_Traffic_Control_Signals_Work
Version:        0.47
Release:        1%{?dist}
Summary:        Explain traffic control signals

License:        GPLv3+
URL:            https://github.com/JohnSauter/How_Traffic_Control_Signals_Work
Source0:        https://github.com/JohnSauter/How_Traffic_Control_Signals_Work/blob/master/How_Traffic_Control_Signals_Work-%{version}.tar.gz
                
BuildArch: noarch

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  python3 >= 3.10
BuildRequires:  git
BuildRequires: graphviz
BuildRequires: inkscape
BuildRequires: python3-shapely
BuildRequires: texlive-scheme-full
BuildRequires: sil-andika-fonts
BuildRequires: sil-charis-fonts
BuildRequires: liberation-mono-fonts
BuildRequires: parallel

%global _hardened_build 1

%description
Explain how traffic control signals work using finite state machines
equipped with timers, toggles to communicate with each other,
and system programs to coordinate between them.

%prep
%autosetup -S git

%build

%configure

%make_build

%install
%make_install

%check
make check VERBOSE=1

%files
%defattr(-,root,root)
%exclude /usr/share/doc/%{name}/AUTHORS
%exclude /usr/share/doc/%{name}/COPYING
%exclude /usr/share/doc/%{name}/ChangeLog
%exclude /usr/share/doc/%{name}/INSTALL
%exclude /usr/share/doc/%{name}/NEWS
%exclude /usr/share/doc/%{name}/README
%exclude /usr/share/doc/%{name}/LICENSE
%doc traffic_control_signals.pdf
%doc AUTHORS ChangeLog NEWS README
%license LICENSE
%license COPYING

%changelog
 * Sat Aug 30 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.47-1 improve green state
 * Sat Aug 23 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.46-1 Start four corners example
 * Sat Aug 23 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.45-1 Add forgotten lamp colors to the renderer.
 * Sun Aug 10 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.44-1 Rewrite green.
 * Sun Aug 10 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.43-1 Fix Makefile.am
 * Sat Aug 02 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.42-1 Improve background.
 * Sun Jul 20 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.41-1 Add bridge.
 * Sun Jul 13 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.40-1 draw_background and simulate_traffic.
 * Sun Jul 06 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.39-1 divide the software into five parts.
 * Fri Jul 04 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.38-1 improve safety_check
 * Sun Jun 29 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.37-1 add safety_check, finish work on flashing
 * Sun Jun 15 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.36-1 continue work on flashing
 * Tue Jun 10 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.35-1 continue work on flashing
 * Sun Jun 08 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.34-1 fix flashing
 * Sat May 17 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.33-1 fix starvation
 * Sat May 10 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.32-1 improve right turn on red
 * Sat May 10 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.31-1 per-vehicle permissive pause
 * Sun May 04 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.30-1 improve document
 * Sat May 03 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.29-1 Wait for gap when conflicting traffic appears.
 * Sat Apr 26 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.28-1 Continue work on right turn on red.
 * Sat Apr 19 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.27-1 Work on passing permissive red signals.
 * Sat Apr 12 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.26-1 Work on passing permissive yellow signals.
 * Sat Apr 04 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.25-1 Improve spawning.
 * Sun Mar 30 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.24-1 improve J lane.
 * Sat Mar 29 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.23-1 in animation: display countdown and compute duration.
 * Sat Mar 22 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.22-1 Don't follow so closely.
 * Sat Mar 15 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.21-1 Make vehicles feel each other.
 * Sun Mar 09 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.20-1 Work on animation.
 * Sun Mar 02 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.19-1 Improve animation structure.
 * Sat Feb 22 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.18-1 Continue work on conversion to two-dimensional.
 * Sat Feb 15 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.16-1 Continue work on conversion to two-dimensional.
 * Sat Feb 08 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.15-1 Continue work on conversion to two-dimensional.
 * Sun Feb 02 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.14-1 Make milestones two-dimensional.
 * Sat Jan 25 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.13-1 More work on the animation.
 * Sun Jan 19 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.12-1 More work on the animation.
 * Sun Jan 12 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.11-1 More work on the animation.
 * Sat Jan 04 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.10-1 More work on the animation.
 * Wed Jan 01 2025 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.9-1 Work on the animation.
 * Mon Dec 30 2024 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.8-1 Start work on the renderer.
 * Sun Dec 29 2024 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.7-1 Through lanes move at full speed in the intersection.
 * Wed Dec 25 2024 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.6-1 Vehicles and pedestrians work.
 * Mon Dec 23 2024 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.5-1 Start work on vehicles and pedestrians.
 * Sun Dec 22 2024 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.4-1 Improve consistency of log output for make check.
 * Sat Dec 21 2024 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.3-1 Improve overlap of green signals
 * Sun Dec 15 2024 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.2-1 I work on it as I have time.
 * Sat Nov 30 2024 John Sauter <John_Sauter@systemeyescomputerstore.com>
 - 0.1-1 Initial version.
