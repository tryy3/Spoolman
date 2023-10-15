import { BaseKey, LiveEvent, LiveProvider } from "@refinedev/core";

/**
 * Converts an API URL to a WebSocket URL.
 * E.g. "https://example.com/api/v1/..." -> "ws://example.com/api/v1/..."
 * or "/api/v1/..." -> "ws://example.com/api/v1/..."
 * @param apiUrl The API URL to convert
 * @returns The WebSocket URL
 */
function toWebsocketURL(apiUrl: string) {
    if (apiUrl[0] === "/") {
        // Relative URL, e.g. "/api/v1/..."

        // Get the current browser URL
        const currentURL = window.location.href;

        // Split the URL to separate the protocol, host, and path
        const urlParts = currentURL.split('/');
        const host = urlParts[2];

        // Create the WebSocket URL by adding "ws://" as the protocol and the relative URL as the path
        return `ws://${host}${apiUrl}`;
    }
    else {
        // Absolute URL, e.g. "https://example.com/api/v1/..."

        // Replace the protocol with "ws://"
        return apiUrl.replace(/^http/, 'ws');
    }
}

/**
 * Subscribes to a single resource.
 * @param apiUrl The API URL
 * @param channel The channel name, not really used
 * @param resource The resource name
 * @param id The ID of the resource
 * @param callback The callback to call when the resource is updated
 * @returns A function to unsubscribe from the resource
 */
function subscribeSingle(apiUrl: string, channel: string, resource: string, id: BaseKey, callback: (event: LiveEvent) => void) {
    // Verify that WebSockets are supported
    if (!('WebSocket' in window)) {
        console.warn("WebSockets are not supported in this browser. Live updates will not be available.");
        return () => { };
    }

    const websocketURL = toWebsocketURL(`${apiUrl}/${resource}/${id}`);

    const ws = new WebSocket(websocketURL);
    ws.onmessage = (message) => {
        const liveEvent: LiveEvent = {
            channel: channel,
            type: "updated",
            payload: {
                data: JSON.parse(message.data),
                ids: [id],
            },
            date: new Date(),
        }

        callback(liveEvent);
    };

    return () => {
        ws.close();
    };
}

const liveProvider = (
    apiUrl: string,
): LiveProvider => ({
    subscribe: ({ channel, params, callback }) => {
        const {
            resource,
            subscriptionType,
            id,
            ids,
        } = params ?? {};

        if (!subscriptionType) {
            throw new Error(
                "[useSubscription]: `subscriptionType` is required in `params`",
            );
        }

        if (!resource) {
            throw new Error(
                "[useSubscription]: `resource` is required in `params`",
            );
        }

        let idList: BaseKey[];
        if (ids) idList = ids;
        else if (id) idList = [id];
        else throw new Error(
            "[useSubscription]: `id` or `ids` is required in `params`",
        );

        return idList.map((id) => {
            return subscribeSingle(apiUrl, channel, resource, id, callback);
        });
    },
    unsubscribe: (closers: (() => void)[]) => {
        closers.forEach((fn) => fn());
    },
})

export default liveProvider;