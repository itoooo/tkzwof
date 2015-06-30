import array
from ryu.base.app_manager import RyuApp
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.lib.packet import packet
from ryu.lib.packet.ethernet import ethernet
from ryu.ofproto import ofproto_v1_3


def insert_packet_in_flow(dp):
    ofproto = dp.ofproto
    ofproto_parser = dp.ofproto_parser

    # create wildcard match
    match = ofproto_parser.OFPMatch()

    # defined in 'ofproto_v1_3.OFPP_CONTROLLER'
    controller_port_no = ofproto.OFPP_CONTROLLER

    # defined in 'ofproto_v1_3_parser.OFPActionOutput'
    output_action = ofproto_parser.OFPActionOutput(controller_port_no)

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
                                         out_port = 0,
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

        insert_packet_in_flow(datapath)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        dp = ev.msg.datapath
        msg = ev.msg

        pkt = packet.Packet(array.array('B', ev.msg.data))
        ether = pkt.get_protocol(ethernet)
        self.logger.info("[dp:%d] in_port: %d, 0x%x %s %s", dp.id,
                                                          msg.match["in_port"],
                                                          ether.ethertype,
                                                          ether.src,
                                                          ether.dst)