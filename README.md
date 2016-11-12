# XenServer 7.0 Ansible

## module: xen_stat

## Example
- xen_stat: vm=VirtualMachineName
  register: st
- fail: msg="Exepected to be 'Running'"
  when: st.xen_stat.power_state != 'Running'
