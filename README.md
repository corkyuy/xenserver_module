# XenServer 7.0 Ansible

## module: xen_control

## Example
'''
- xen_control: vm=VirtualMachineName
  register: st
- fail: msg="Exepected to be 'Running'"
  when: st.xen_control.power_state != 'Running'
'''
