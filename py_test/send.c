
void SendData2Toi(const char* msg,size_t len)
{

    unsigned m_socket = socket(AF_INET, SOCK_DGRAM, 0);
    struct sockaddr_in localaddr;
    bzero(&localaddr, sizeof(localaddr));
    localaddr.sin_family = AF_INET;
    localaddr.sin_addr.s_addr = inet_addr("127.0.0.1");
    localaddr.sin_port = htons(localport);
    bind(m_socket, (struct sockaddr*)&localaddr, sizeof(localaddr));
    struct sockaddr_in m_dest_addr;
    m_dest_addr.sin_family = AF_INET;
    m_dest_addr.sin_port = htons(50001);
    inet_aton("127.0.0.1",&m_dest_addr.sin_addr);
    sendto(m_socket,msg,len,0,(struct sockaddr*)&m_dest_addr,sizeof(struct sockaddr_in));


}
