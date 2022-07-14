# 1 Quick start for ZCU102 Custom PYNQ v2.6 Image Building

## 1.0 Preparation fo the directory
 * $ git clone https://github.com/Xilinx/PYNQ.git
 * $ git checkout -b image_v2.6.0
 * Replace Makefile with that at <PYNQ repository>/sdbuild/Makefile
 * Replace setup_host.sh with that at <PYNQ repository>/sdbuild/scripts
 
## 1.1 Use existing Ubuntu OS for ZCU102 v2.6
 * Ensure that sudo is configured for passwordless use and that proxy settings and other environment variables are forwarded correctly.
 * Install Petalinux 2020.1
 * Install Vivado/Vitis 2020.1
 * Ensure that Petalinux and Vitis is on the PATH
 * Run <PYNQ repository>/sdbuild/scripts/setup_host.sh

## 1.2 Source the appropriate settings for PetaLinux and Vitis
 * $ source <path-to-vitis>/Vivado/2020.1/settings64.sh
 * $ source <path-to-vitis>/Vitis/2020.1/settings64.sh
 * $ source <path-to-petalinux>/petalinux/2020.1/settings.sh
 * $ petalinux-util --webtalk off

## 1.3 Building the Image for ZCU102 v2.6 using the prebuilt board-agnostic image
 * Download the prebuilt board-agnostic image of aarch64 v2.6 for Zynq UltraScale+ from [HERE](https://bit.ly/pynq_rootfs_aarch64_v2_6).
 * Download the BSP for ZCU102 Zynq UltraScale+ from [XILINX_WEBSITE](https://www.xilinx.com/member/forms/download/xef.html?filename=xilinx-zcu102-v2020.1-final.bsp).
 * Move both downloaded files (bionic.aarch64.2.6.0_2020_10_19.img and xilinx-zcu102-v2020.1-final.bsp) to the target directory <PYNQ repository>/sdbuild/
 * $ cd <PYNQ repository>/sdbuild/
 * Run `"bash scripts/image_from_prebuilt.sh ZCU102 xilinx-zcu102-v2020.1-final.bsp aarch64 bionic.aarch64.2.6.0_2020_10_19.img"` to recreate ZCU102 board image.
 * Wait for a couple of minutes or hour(s). Once completed, check for the ZCU102 image (ZCU102-2.6.0.img) at <PYNQ repository>/sdbuild/output.
