Name: waldur-openstack
Summary: OpenStack plugin for Waldur
Group: Development/Libraries
Version: 0.31.1
Release: 1.el7
License: MIT
Url: http://waldur.com
Source0: %{name}-%{version}.tar.gz

Requires: waldur-core > 0.139.0
Requires: python-ceilometerclient >= 2.3.0
Requires: python-cinderclient >= 1.6.0
Requires: python-cinderclient < 2.0.0
Requires: python-glanceclient >= 1:2.0.0
Requires: python-iptools >= 0.6.1
Requires: python-keystoneclient >= 1:2.3.1
Requires: python-neutronclient >= 4.1.1
Requires: python-novaclient >= 1:3.3.0
Requires: python-novaclient < 1:3.4.0

Obsoletes: nodeconductor-openstack

BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires: python-setuptools

%description
OpenStack plugin for Waldur.

%prep
%setup -q -n %{name}-%{version}

%build
python setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 --root=%{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{python_sitelib}/*

%changelog
* Fri Jul 14 2017 Jenkins <jenkins@opennodecloud.com> - 0.31.1-1.el7
- New upstream release

* Wed Jul 12 2017 Jenkins <jenkins@opennodecloud.com> - 0.31.0-1.el7
- New upstream release

* Mon Jul 3 2017 Jenkins <jenkins@opennodecloud.com> - 0.30.2-1.el7
- New upstream release

* Fri Jun 30 2017 Jenkins <jenkins@opennodecloud.com> - 0.30.1-1.el7
- New upstream release

* Thu Jun 22 2017 Jenkins <jenkins@opennodecloud.com> - 0.30.0-1.el7
- New upstream release

* Fri Jun 9 2017 Jenkins <jenkins@opennodecloud.com> - 0.29.0-1.el7
- New upstream release

* Fri Jun 2 2017 Jenkins <jenkins@opennodecloud.com> - 0.28.0-1.el7
- New upstream release

* Wed May 31 2017 Jenkins <jenkins@opennodecloud.com> - 0.27.0-1.el7
- New upstream release

* Wed May 17 2017 Jenkins <jenkins@opennodecloud.com> - 0.26.0-1.el7
- New upstream release

* Sat May 6 2017 Jenkins <jenkins@opennodecloud.com> - 0.25.0-1.el7
- New upstream release

* Sun Apr 23 2017 Jenkins <jenkins@opennodecloud.com> - 0.24.0-1.el7
- New upstream release

* Fri Apr 14 2017 Jenkins <jenkins@opennodecloud.com> - 0.23.2-1.el7
- New upstream release

* Wed Apr 12 2017 Jenkins <jenkins@opennodecloud.com> - 0.23.1-1.el7
- New upstream release

* Tue Apr 11 2017 Jenkins <jenkins@opennodecloud.com> - 0.23.0-1.el7
- New upstream release

* Fri Apr 7 2017 Jenkins <jenkins@opennodecloud.com> - 0.22.1-1.el7
- New upstream release

* Fri Mar 31 2017 Jenkins <jenkins@opennodecloud.com> - 0.22.0-1.el7
- New upstream release

* Wed Mar 15 2017 Jenkins <jenkins@opennodecloud.com> - 0.21.0-1.el7
- New upstream release

* Wed Mar 15 2017 Jenkins <jenkins@opennodecloud.com> - 0.20.0-1.el7
- New upstream release

* Thu Mar 2 2017 Jenkins <jenkins@opennodecloud.com> - 0.19.2-1.el7
- New upstream release

* Mon Feb 20 2017 Jenkins <jenkins@opennodecloud.com> - 0.19.1-1.el7
- New upstream release

* Sat Feb 18 2017 Jenkins <jenkins@opennodecloud.com> - 0.19.0-1.el7
- New upstream release

* Wed Feb 15 2017 Jenkins <jenkins@opennodecloud.com> - 0.18.0-1.el7
- New upstream release

* Wed Feb 8 2017 Jenkins <jenkins@opennodecloud.com> - 0.17.0-1.el7
- New upstream release

* Mon Feb 6 2017 Jenkins <jenkins@opennodecloud.com> - 0.16.0-1.el7
- New upstream release

* Thu Feb 2 2017 Jenkins <jenkins@opennodecloud.com> - 0.15.3-1.el7
- New upstream release

* Thu Jan 26 2017 Jenkins <jenkins@opennodecloud.com> - 0.15.2-1.el7
- New upstream release

* Wed Jan 25 2017 Jenkins <jenkins@opennodecloud.com> - 0.15.1-1.el7
- New upstream release

* Tue Jan 24 2017 Jenkins <jenkins@opennodecloud.com> - 0.15.0-1.el7
- New upstream release

* Mon Jan 23 2017 Jenkins <jenkins@opennodecloud.com> - 0.14.3-1.el7
- New upstream release

* Wed Jan 18 2017 Jenkins <jenkins@opennodecloud.com> - 0.14.2-1.el7
- New upstream release

* Tue Jan 17 2017 Jenkins <jenkins@opennodecloud.com> - 0.14.1-1.el7
- New upstream release

* Tue Jan 17 2017 Jenkins <jenkins@opennodecloud.com> - 0.14.0-1.el7
- New upstream release

* Sun Jan 15 2017 Jenkins <jenkins@opennodecloud.com> - 0.13.0-1.el7
- New upstream release

* Sat Jan 14 2017 Juri <juri@opennodecloud.com> - 0.12.1-1.el7
- New upstream release

* Tue Jan 3 2017 Jenkins <jenkins@opennodecloud.com> - 0.12.0-1.el7
- New upstream release

* Mon Dec 19 2016 Jenkins <jenkins@opennodecloud.com> - 0.11.0-1.el7
- New upstream release

* Wed Dec 14 2016 Jenkins <jenkins@opennodecloud.com> - 0.10.0-1.el7
- New upstream release

* Mon Oct 31 2016 Jenkins <jenkins@opennodecloud.com> - 0.9.1-1.el7
- New upstream release

* Thu Oct 27 2016 Jenkins <jenkins@opennodecloud.com> - 0.9.0-1.el7
- New upstream release

* Wed Oct 26 2016 Jenkins <jenkins@opennodecloud.com> - 0.8.0-1.el7
- New upstream release

* Thu Oct 20 2016 Jenkins <jenkins@opennodecloud.com> - 0.7.1-1.el7
- New upstream release

* Tue Sep 27 2016 Jenkins <jenkins@opennodecloud.com> - 0.7.0-1.el7
- New upstream release

* Fri Sep 16 2016 Jenkins <jenkins@opennodecloud.com> - 0.6.0-1.el7
- New upstream release

* Thu Aug 18 2016 Jenkins <jenkins@opennodecloud.com> - 0.5.5-1.el7
- New upstream release

* Sun Aug 14 2016 Jenkins <jenkins@opennodecloud.com> - 0.5.4-1.el7
- New upstream release

* Fri Aug 12 2016 Jenkins <jenkins@opennodecloud.com> - 0.5.3-1.el7
- New upstream release

* Thu Aug 4 2016 Jenkins <jenkins@opennodecloud.com> - 0.5.2-1.el7
- New upstream release

* Thu Jul 28 2016 Jenkins <jenkins@opennodecloud.com> - 0.5.1-1.el7
- New upstream release

* Fri Jul 15 2016 Jenkins <jenkins@opennodecloud.com> - 0.5.0-1.el7
- New upstream release

* Thu Jul 7 2016 Jenkins <jenkins@opennodecloud.com> - 0.4.10-1.el7
- New upstream release

* Thu Jul 7 2016 Jenkins <jenkins@opennodecloud.com> - 0.4.9-1.el7
- New upstream release

* Wed Jul 6 2016 Jenkins <jenkins@opennodecloud.com> - 0.4.8-1.el7
- New upstream release

* Tue Jul 5 2016 Jenkins <jenkins@opennodecloud.com> - 0.4.7-1.el7
- New upstream release

* Tue Jul 5 2016 Jenkins <jenkins@opennodecloud.com> - 0.4.6-1.el7
- New upstream release

* Mon Jul 4 2016 Jenkins <jenkins@opennodecloud.com> - 0.4.5-1.el7
- New upstream release

* Thu Jun 30 2016 Jenkins <jenkins@opennodecloud.com> - 0.4.4-1.el7
- New upstream release

* Thu Jun 30 2016 Jenkins <jenkins@opennodecloud.com> - 0.4.3-1.el7
- New upstream release

* Thu Jun 30 2016 Jenkins <jenkins@opennodecloud.com> - 0.4.2-1.el7
- New upstream release

* Thu Jun 30 2016 Jenkins <jenkins@opennodecloud.com> - 0.4.1-1.el7
- New upstream release

* Wed Jun 29 2016 Jenkins <jenkins@opennodecloud.com> - 0.4.0-1.el7
- New upstream release

* Tue May 24 2016 Jenkins <jenkins@opennodecloud.com> - 0.3.0-1.el7
- New upstream release

* Mon May 16 2016 Jenkins <jenkins@opennodecloud.com> - 0.2.0-1.el7
- New upstream release

* Mon May 16 2016 Ilja Livenson <ilja@opennodecloud.com> - 0.1.0-1.el7
- Initial version of the package
