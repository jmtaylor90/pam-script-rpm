%global commit 1bb6718fa767107e97893c5fe538420ef249b0a0
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global _hardened_build 1
%global upstream_name pam-script

Name:           pam_script
Version:        1.1.7
Release:        1%{?dist}
Summary:        PAM module for executing scripts

Group:          Applications/System
License:        GPLv2
URL:            https://github.com/jeroennijhof/pam_script
Source0:        https://github.com/jeroennijhof/pam_script/archive/%{commit}/%{upstream_name}-%{commit}.tar.gz

%{?el5:BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)}

BuildRequires:  pam-devel 

%description
pam_script is a module which allows to execute scripts after opening
and/or closing a session using PAM.

%prep
%setup -q -n pam-script-1.1.7
cp etc/README etc/README.module_types
cp fedora/configure.fedora configure

%build
%configure --libdir=/%{_lib}/security
make %{?_smp_mflags}

cd -

%install
%{?el5:rm -rf %{buildroot}}
make install DESTDIR=%{buildroot}

rm %{buildroot}%{_sysconfdir}/README

%{?el5:%clean}
%{?el5:rm -rf %{buildroot}}

%posttrans
# apply new SELinux file context
restorecon %{_sysconfdir}/pam_script*
restorecon %{_sysconfdir}/pam-script.d/

%files
%doc AUTHORS COPYING ChangeLog README NEWS etc/README.module_types etc/README.pam_script 
%dir %{_sysconfdir}/pam-script.d/
%{_sysconfdir}/pam_script*
/%{_lib}/security/*
%{_mandir}/man7/%{upstream_name}.7*

%changelog
* Sun May 11 2014 Jason Taylor <jason.taylor@secure-24.com> - 1.1.7-1
- Initial Build
