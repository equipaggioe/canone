import com.sun.net.httpserver.HttpServer;
import java.net.InetAddress;
import java.net.InetSocketAddress;

// The piece of java.sh: answers 204 on loopback.
public class Ping {
  public static void main(String[] args) throws Exception {
    var server =
        HttpServer.create(new InetSocketAddress(InetAddress.getLoopbackAddress(), 8099), 0);
    server.createContext(
        "/",
        exchange -> {
          exchange.sendResponseHeaders(204, -1);
          exchange.close();
        });
    server.start();
  }
}
