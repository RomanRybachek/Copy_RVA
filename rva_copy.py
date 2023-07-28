import idaapi
import idc
import time

import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
from PyQt5.Qt import QApplication

PLUGIN_NAME = "Copy RVA"
PLUGIN_HOTKEY = ''

class rva_copy(idaapi.plugin_t):

    flags = idaapi.PLUGIN_PROC | idaapi.PLUGIN_HIDE
    comment = "Copy RVA under cursor"
    wanted_name = PLUGIN_NAME
    wanted_hotkey = PLUGIN_HOTKEY


    def init(self):

        self._init_action_copy_bytes()
        self._init_hooks()

        idaapi.msg("%s initialized...\n" % (self.wanted_name))
        return idaapi.PLUGIN_KEEP

    def run(self, arg):
        idaapi.msg("%s cannot be run as a script.\n" % self.wanted_name)


    def term(self):
        self._hooks.unhook()
        self._del_action_copy_bytes()

        idaapi.msg("%s terminated...\n" % self.wanted_name)

    def _init_hooks(self):
        self._hooks = Hooks()
        self._hooks.ready_to_run = self._init_hexrays_hooks
        self._hooks.hook()

    def _init_hexrays_hooks(self):
        if idaapi.init_hexrays_plugin():
            idaapi.install_hexrays_callback(self._hooks.hxe_callback)

    ACTION_COPY_RVA  = "prefix:copy_rva"

    def _init_action_copy_bytes(self):
        action_desc = idaapi.action_desc_t(
            self.ACTION_COPY_RVA,         
            "Copy RVA",                   
            IDACtxEntry(copy_rva),        
            PLUGIN_HOTKEY,
            "Copy RVA under cursor",
            31
        )
        assert idaapi.register_action(action_desc), "Action registration failed"


    def _del_action_copy_bytes(self):
        idaapi.unregister_action(self.ACTION_COPY_RVA)
        pass

def PLUGIN_ENTRY():
    return rva_copy()

def copy_rva():
    ea = idc.get_screen_ea()
    base = idaapi.get_imagebase()
    rva = hex(ea - base)
    
    QApplication.clipboard().setText(rva)
    print("RVA was copied:", rva)

class IDACtxEntry(idaapi.action_handler_t):

    def __init__(self, action_function):
        idaapi.action_handler_t.__init__(self)
        self.action_function = action_function

    def activate(self, ctx):
        self.action_function()
        return 1

    def update(self, ctx):
        return idaapi.AST_ENABLE_ALWAYS

def inject_hex_copy_actions(form, popup, form_type):

    if form_type == idaapi.BWN_DISASMS:

        idaapi.attach_action_to_popup(
            form,
            popup,
            rva_copy.ACTION_COPY_RVA,
            "Copy RVA",
            idaapi.SETMENU_APP
        )

    return 0

class Hooks(idaapi.UI_Hooks):

    def finish_populating_widget_popup(self, widget, popup):
        inject_hex_copy_actions(widget, popup, idaapi.get_widget_type(widget))
        return 0

    def finish_populating_tform_popup(self, form, popup):
        inject_hex_copy_actions(form, popup, idaapi.get_tform_type(form))
        return 0

    def hxe_callback(self, event, *args):
        if event == idaapi.hxe_populating_popup:
            form, popup, vu = args

            idaapi.attach_action_to_popup(
                form,
                popup,
                rva_copy.ACTION_COPY_RVA,
                "Copy RVA",
                idaapi.SETMENU_APP,
            )

        return 0