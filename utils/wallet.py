import streamlit.components.v1 as components

def solana_connect_button():
    """
    Injects a Phantom Connect button that communicates the wallet address
    back to Streamlit via URL query parameters.
    """
    
    html_code = """
    <div id="root">
        <button id="connect-btn" style="
            width: 100%;
            padding: 12px;
            background-color: #000000;
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            font-size: 14px;
        ">
            Sign in with Phantom
        </button>
    </div>

    <script>
        const btn = document.getElementById('connect-btn');
        
        btn.addEventListener('click', async () => {
            if (window.solana && window.solana.isPhantom) {
                try {
                    btn.innerText = "Connecting...";
                    const resp = await window.solana.connect();
                    const publicKey = resp.publicKey.toString();
                    
                    // Update URL query parameters to trigger Streamlit reload
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set('wallet', publicKey);
                    window.parent.location.href = url.href;
                    
                } catch (err) {
                    console.error(err);
                    btn.innerText = "Sign in with Phantom";
                }
            } else {
                alert("Phantom Wallet not found! Please install the extension.");
                window.open("https://phantom.app/", "_blank");
            }
        });
    </script>
    """
    return components.html(html_code, height=60)
