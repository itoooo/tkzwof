from ryu.base.app_manager import RyuApp
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER
from ryu.ofproto import ofproto_v1_3


def del_all_flow(dp):
    match = dp.ofproto_parser.OFPMatch()
    mod = dp.ofproto_parser.OFPFlowMod(
        datapath=dp,
        table_id=0,
        match=match,
        out_port=dp.ofproto.OFPP_ANY, out_group=dp.ofproto.OFPG_ANY,
        command=dp.ofproto.OFPFC_DELETE)
    dp.send_msg(mod)


def add_patch_flow(dp, in_port_no, out_port_no):
    ofproto = dp.ofproto
    ofproto_parser = dp.ofproto_parser

    match = ofproto_parser.OFPMatch(in_port = in_port_no)

    output_action = ofproto_parser.OFPActionOutput(out_port_no)

    inst = ofproto_parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                                actions = [output_action])

    flow_mod = ofproto_parser.OFPFlowMod(datapath = dp,
                                         cookie = 0,
                                         cookie_mask = 0,
                                         table_id = 0,
                                         command = ofproto.OFPFC_ADD,
                                         idle_timeout = 0,
                                         hard_timeout = 0,
                                         priority = ofproto.OFP_DEFAULT_PRIORITY,
                                         buffer_id = ofproto.OFP_NO_BUFFER,
                                         out_port = out_port_no,
                                         out_group = 0,
                                         flags = 0,
                                         match = match,
                                         instructions = [inst])
    dp.send_msg(flow_mod)


class PacketIn(RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(PacketIn, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_feature_handler(self, ev):
        datapath = ev.msg.datapath

        self.logger.info("datapath: %d connected.", datapath.id)

        del_all_flow(datapath)
        add_patch_flow(datapath, 3, 4)
        add_patch_flow(datapath, 4, 3)
