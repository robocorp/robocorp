import { logError } from './helpers';

/**
 * A socket.io-like interface for websockets.
 *
 * Not really using socket.io because of instability issues
 * using it (and it was hard to reason why it didn't work
 * properly when it didn't work properly).
 */
export class WebsocketConn {
  /**
   * The actual websocket connection (set after connect())
   */
  private ws: WebSocket | null = null;

  /**
   * Flag indicating whether it's already connected.
   */
  private connected = false;

  /**
   * Flag indicating whether it's currently connecting.
   */
  private connecting = false;

  /**
   * Handlers to manage received events.
   */
  private eventToHandlers: Map<string, any[]> = new Map();

  /**
   * Buffer with the messages to be sent to the server
   * (i.e.: if not currently connected, messages will be buffered
   * so that they're sent when a connection is made).
   */
  private messages: string[] = [];

  /**
   * Just creates the websocket connection, doesn't really connect at this point.
   *
   * @param url The websocket url to connect to.
   */
  constructor(private url: string) {
    this.url = url;
  }

  /**
   * Registers a handler to some event.
   */
  public on(event: string, handler: any) {
    let handlers = this.eventToHandlers.get(event);
    if (!handlers) {
      handlers = [];
      this.eventToHandlers.set(event, handlers);
    }
    handlers.push(handler);
  }

  /**
   * Notifies handlers of some event.
   */
  private notify(event: string, ...args: any[]) {
    const handlers = this.eventToHandlers.get(event);
    if (handlers) {
      for (const handler of handlers) {
        // console.log('notify', event, handler, args);
        try {
          handler(...args);
        } catch (err) {
          logError(err);
        }
      }
    }
  }

  /**
   * Emits an event to the server.
   */
  public async emit(event: string, data: any = undefined) {
    const msg: any = { event: event };
    if (data !== undefined) {
      msg.data = data;
    }
    this.messages.push(msg);
    await this.processMessages();
  }

  private async processMessages() {
    if (this.connected && this.ws) {
      while (this.messages.length > 0) {
        try {
          // That's sync but it doesn't block (just enqueues data to send).
          this.ws.send(JSON.stringify(this.messages[0]));

          // If it was sent, remove it from the messages to send.
          this.messages.shift();
        } catch (err) {
          // unable to send
          logError(err);
          break; // Retry later.
        }
      }
    }
  }

  public connect(): Promise<void> | void {
    if (this.connecting) {
      // console.log('Websocket: connect ignored (already connecting).');
      return;
    }
    if (this.connected) {
      // console.log('Websocket: connect ignored (already connected).');
      return;
    }
    // console.log('Websocket: starting connection.');
    this.connecting = true;
    return new Promise((resolve, reject) => {
      // console.log('Websocket: connecting to: ', this.url);
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        // console.log('Websocket: connection opened (marking as connected)');
        this.connected = true;
        this.connecting = false;
        this.notify('connect');
        resolve();
      };

      this.ws.onmessage = this.handleMessage;
      this.ws.onclose = this.handleClose;
      const markNotConnectingAndReject = () => {
        // console.log('Websocket: connection on error');
        this.connected = false;
        this.connecting = false;
        this.notify('disconnect');
        reject();
      };
      this.ws.onerror = markNotConnectingAndReject;
    });
  }

  /**
   * Messages is received from the server.
   */
  private handleMessage = (message: MessageEvent) => {
    const dataStr = message.data;
    if (dataStr) {
      // console.log('Received data', dataStr);
      const obj = JSON.parse(dataStr);
      const event = obj['event'];
      const data = obj['data'];
      if (event) {
        if (data !== undefined) {
          this.notify(event, data);
        } else {
          this.notify(event);
        }
      }
    }
  };

  /**
   * Note: after starting the connection, handleClose
   * is always called even if it doesn't connect
   * (so, it's used as a way to re-connect later on).
   */
  private handleClose = () => {
    // console.log('closing');
    this.connected = false;
    this.connecting = false;
    this.ws = null;

    // Auto-reconnect in a short time as the connection was
    // broken for some reason.
    setTimeout(() => {
      this.connect();
    }, 5000);
  };
}
