PYTHON3_PYSERIAL_VERSION = 3.5
PYTHON3_PYSERIAL_SOURCE = pyserial-$(PYTHON3_PYSERIAL_VERSION).tar.gz
PYTHON3_PYSERIAL_SITE = https://files.pythonhosted.org/packages/source/p/pyserial
PYTHON3_PYSERIAL_SETUP_TYPE = setuptools
PYTHON3_PYSERIAL_LICENSE = BSD-3-Clause
PYTHON3_PYSERIAL_LICENSE_FILES = LICENSE.txt

define PYTHON3_PYSERIAL_INSTALL_TARGET_CMDS
    cd $(BUILD_DIR)/python3-pyserial-$(PYTHON3_PYSERIAL_VERSION) && \
    $(TARGET_MAKE_ENV) $(HOST_DIR)/bin/python3 setup.py install --prefix=/usr --root=$(TARGET_DIR)
    touch $(TARGET_DIR)/usr/lib/python3.13/site-packages/serial/__init__.py
endef

$(eval $(python-package))

