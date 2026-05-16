import streamlit as st
import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Ultra Pro Max - Final Scanner", layout="wide")
st_autorefresh(interval=60000, key="final_scanner_refresh")

# Custom CSS for Professional UI
st.markdown("""
<style>
    .header {background: linear-gradient(135deg, #0f172a, #1e40af); padding: 20px; border-radius: 12px; color: white; text-align: center;}
    .section {padding: 10px; border-radius: 8px; color: white; font-weight: bold; text-align: center; margin-bottom: 8px;}
    .blue {background: #2563eb;} .green {background: #16a34a;} .purple {background: #9333ea;} 
    .orange {background: #f97316;} .cyan {background: #0891b2;} .dark-red {background: #991b1b;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>Smart Scanner Ultra Pro Max</h1><p>Full Analysis: Breakouts | Momentum | CPR | Near-BO</p></div>', unsafe_allow_html=True)

# Nifty 200/500 Stocks List
symbols = [
    "ABB.NS", "ACC.NS", "ADANIENT.NS", "ADANIPORTS.NS", "ADANIPOWER.NS", "AMBUJACEM.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS",
    "BAJFINANCE.NS", "BAJAJFINSV.NS", "BANKBARODA.NS", "BEL.NS", "BHARTIARTL.NS", "BPCL.NS", "BRITANNIA.NS", "CANBK.NS", "CIPLA.NS", "COALINDIA.NS",
    "DLF.NS", "DABUR.NS", "DIVISLAB.NS", "DRREDDY.NS", "EICHERMOT.NS", "GAIL.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
    "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS", "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS",
    "M&M.NS", "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS", "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SUNPHARMA.NS",
    "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TCS.NS", "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS", "WIPRO.NS", "ZOMATO.NS", "TRENT.NS",
    "RVNL.NS", "IRFC.NS", "PFC.NS", "RECLTD.NS", "MAZDOCK.NS", "BHEL.NS", "HUDCO.NS", "COFORGE.NS", "PERSISTENT.NS", "DIXON.NS", "MANAPPURAM.NS", "FORTIS.NS"
]

def analyze_stock(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df_hist = ticker.history(period="1y", interval="1d")
        if df_hist.empty or len(df_hist) < 20: return None
        
        last = df_hist.iloc[-1]
        prev = df_hist.iloc[-2]
        
        # 1. Formatting LTP
        ltp = round(float(last['Close']), 2)
        change = round(((last['Close'] - prev['Close']) / prev['Close']) * 100, 2)
        
        # 2. Volume Spike
        avg_vol = df_hist['Volume'].iloc[-6:-1].mean()
        vol_ratio = round(last['Volume'] / avg_vol, 2) if avg_vol > 0 else 0
        
        # 3. Breakout Logic
        high_1w = round(df_hist['High'].iloc[-6:-1].max(), 2)
        high_52w = round(df_hist['High'].iloc[:-1].max(), 2)
        pdh = round(prev['High'], 2)
        
        # 4. Distance for Near Breakout
        dist_52w = round(((high_52w - ltp) / high_52w) * 100, 2)
        
        # 5. CPR Width Details
        h, l, c = prev['High'], prev['Low'], prev['Close']
        pivot = (h + l + c) / 3
        bc = (h + l) / 2
        tc = (pivot - bc) + pivot
        cpr_w = round(abs(tc - bc) / pivot * 100, 3) if pivot > 0 else 0
        
        flash = "⚡ HIGH" if abs(change) > 2.0 else "Normal"
        name = symbol.replace(".NS", "")
        display_name = f"🚨 {name}" if vol_ratio > 2.5 else name
        
        return {
            "Stock": display_name,
            "LTP": ltp,
            "%Chg": change,
            "Flash": flash,
            "CPR_Width": cpr_w,
            "Prev_BO": "✅" if ltp > pdh else "❌",
            "1W_High": high_1w,
            "Dist_52W": dist_52w,
            "Vol_Ratio": vol_ratio,
            "View": f"https://www.tradingview.com/chart/?symbol=NSE:{name}"
        }
    except Exception: 
        return None

# Parallel Scanner Execution (Optimized max_workers for Cloud Deployments)
with st.spinner("Analyzing Market Data..."):
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = [r for r in list(executor.map(analyze_stock, symbols)) if r]

if results:
    df = pd.DataFrame(results)
    st.info(f"🕒 Update: {datetime.now().strftime('%I:%M:%S %p')} | 🚨 = Volume Spike | ✅ = PDH Breakout")

    def style_status(s):
        return ['background-color: #16a34a; color: white; font-weight: bold;' if v == '⚡ HIGH' else '' for v in s]

    col_cfg = {"View": st.column_config.LinkColumn("Chart")}
    
    # --- Row 1: Breakouts ---
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section purple">🚀 52W High & PDH Breakout</div>', unsafe_allow_html=True)
        bo_df = df[df["Prev_BO"] == "✅"].sort_values("%Chg", ascending=False).head(10)
        st.dataframe(bo_df[["Stock", "LTP", "%Chg", "Prev_BO", "View"]], column_config=col_cfg, use_container_width=True, hide_index=True)

    with c2:
        st.markdown('<div class="section cyan">📈 1 Week High Breakout</div>', unsafe_allow_html=True)
        w1_df = df[df["LTP"] > df["1W_High"]].sort_values("%Chg", ascending=False).head(10)
        st.dataframe(w1_df[["Stock", "LTP", "%Chg", "1W_High", "View"]], column_config=col_cfg, use_container_width=True, hide_index=True)

    # --- Row 2: Near Breakout & CPR ---
    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="section orange">🔥 Near Breakout (Watching)</div>', unsafe_allow_html=True)
        near_df = df[(df["Dist_52W"] > 0) & (df["Dist_52W"] < 1.5)].sort_values("Dist_52W").head(10)
        st.dataframe(near_df[["Stock", "LTP", "Dist_52W", "View"]], column_config=col_cfg, use_container_width=True, hide_index=True)

    with c4:
        st.markdown('<div class="section blue">🎯 Narrow CPR (Trending)</div>', unsafe_allow_html=True)
        narrow_df = df.sort_values("CPR_Width").head(10)
        st.dataframe(narrow_df[["Stock", "LTP", "CPR_Width", "%Chg", "View"]], column_config=col_cfg, use_container_width=True, hide_index=True)

    # --- Full Momentum Table ---
    st.markdown("---")
    st.markdown('<div class="section green">🔥 Active Momentum & Volume Spikes</div>', unsafe_allow_html=True)
    momentum_df = df.sort_values(by=["%Chg", "Vol_Ratio"], ascending=False).head(20)
    
    # Modernized Pandas Styler implementation
    st.dataframe(momentum_df[["Stock", "LTP", "%Chg", "Vol_Ratio", "Flash", "View"]].style.apply(style_status, subset=['Flash']), 
                 column_config=col_cfg, use_container_width=True, hide_index=True)
else:
    st.error("No data fetched. Kindly check ticker response or network connection.")