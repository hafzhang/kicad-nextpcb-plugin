from nextPCB_plugin.kicad_pcb.board_manager import BoardManager
from nextPCB_plugin.settings_nextpcb.form_value_fitter import fitter_and_map_form_value
from .process_info_model import ProcessInfoModel
from nextPCB_plugin.utils_nextpcb.form_panel_base import FormKind, FormPanelBase
from nextPCB_plugin.utils_nextpcb.roles import EditDisplayRole
from nextPCB_plugin.settings_nextpcb.setting_manager import SETTING_MANAGER
from nextPCB_plugin.settings_nextpcb.single_plugin import SINGLE_PLUGIN
from nextPCB_plugin.order_nextpcb.supported_region import SupportedRegion

from .ui_process_info import UiProcessInfo
import wx
from collections import defaultdict

IS_PLUG = [
    EditDisplayRole(0, _("No")),
    EditDisplayRole(1, _("Yes")),

]

STEEL_TYPE = [
    EditDisplayRole(0, _("Ordinary Steel Mesh")),
    EditDisplayRole(1, _("Stepped Steel Mesh")),
]


STEEL_FOLLOW_DELIVERY = [
    EditDisplayRole(0, _("No Need")),
    EditDisplayRole(1, _("Need")),
]


class SmtProcessInfoViewNextpcb(UiProcessInfo, FormPanelBase):
    def __init__(self, parent, board_manager: BoardManager):
        super().__init__(parent)
        self.board_manager = board_manager

        self.Fit()
        # self.judge_plug()
        self.is_plug.Bind(wx.EVT_CHOICE, self.judge_plug)
        

    @fitter_and_map_form_value
    def get_from(self, kind: FormKind) -> "dict":
        info = ProcessInfoModel(
            bom_material_type_number= self.bom_material_type_number.GetValue(),
            patch_pad_number = self.patch_pad_number.GetValue(),
            is_plug = IS_PLUG[self.is_plug.GetSelection()].EditRole,
            # self.is_plug.GetStringSelection(),
            plug_number = self.plug_number.GetValue(),
            steel_type = STEEL_TYPE[self.steel_type.GetSelection()].EditRole, 
            is_steel_follow_delivery = STEEL_FOLLOW_DELIVERY[  self.is_steel_follow_delivery.GetSelection()].EditRole, 

        )
        return vars(info)

    def init(self):
        self.initUI()
        self.GetPatchPadCount()

    def initUI(self):
        self.is_plug.Append( [i.DisplayRole for i in IS_PLUG] )
        self.is_plug.SetSelection(0)
 
        self.steel_type.Append( [i.DisplayRole for i in STEEL_TYPE] )
        self.steel_type.SetSelection(0)
 
        self.is_steel_follow_delivery.Append( [i.DisplayRole for i in STEEL_FOLLOW_DELIVERY] )
        self.is_steel_follow_delivery.SetSelection(0)
        
        self.bom_material_type_number.SetValue("0")
        self.patch_pad_number.SetValue("0")
        self.plug_number.SetValue("0")

    def SetValueFpGuoupCount(self, unique_value_fp_count):
        self.bom_material_type_number.SetValue( str( unique_value_fp_count) )
        
    def GetPatchPadCount(self):
        pads = self.board_manager.board.GetPads()
    
        # 使用defaultdict来自动初始化计数为0
        attrib_counts = defaultdict(int, {'PTH': 0, 'SMD': 0})
        
        # PAD_ATTRIB中各属性的值
        PAD_ATTRIB_VALUES = {
            0: 'PTH',
            1: 'SMD',
            2: 'CONN',
            3: 'NPTH'
        }
        
        for pad in pads:
            attrib = pad.GetAttribute()
            # 直接使用PAD_ATTRIB中的键来增加计数
            if attrib in PAD_ATTRIB_VALUES:
                attrib_name = PAD_ATTRIB_VALUES[attrib]
                attrib_counts[attrib_name] += 1
        
        self.patch_pad_number.SetValue(str( attrib_counts['SMD'] ))
        if attrib_counts['PTH'] != 0:
            self.is_plug.SetSelection(1)
            self.plug_number.SetValue(str( attrib_counts['PTH'] ))


    def on_region_changed(self):
        for i in self.is_steel_follow_delivery, self.is_steel_follow_delivery_label:
            i.Show( False )
        self.Layout()

    def judge_plug(self,evt=None):
        for i in self.plug_number, self.plug_number_label :
            i.Show( self.is_plug.GetSelection() != 0 )
        self.Layout()
        SINGLE_PLUGIN.get_main_wind().smt_adjust_size()

