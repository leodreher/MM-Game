import streamlit as st
import pandas as pd

# Initialize session state
if 'trades' not in st.session_state:
    st.session_state.trades = []
if 'bids' not in st.session_state:
    st.session_state.bids = []

st.title("Market Making Game")

# initialize hints defaults in session state
if 'hint1' not in st.session_state:
    st.session_state.hint1 = ""
if 'hint2' not in st.session_state:
    st.session_state.hint2 = ""
if 'hint3' not in st.session_state:
    st.session_state.hint3 = ""

# Context
all_hints = " | ".join([h for h in [st.session_state.hint1, st.session_state.hint2, st.session_state.hint3] if h.strip()])
if all_hints:
    st.markdown(f"*Hints:* {all_hints}")
else:
    st.markdown("*Hints:* (Enter sector, revenue, and outstanding shares on Tab 1)")
steps = ["1. Setup (Keep hidden!)", "2. Bidding", "3. Market Maker", "4. Trading", "5. Resolution"]
if 'selected_tab' not in st.session_state:
    st.session_state.selected_tab = 0

sel = st.radio("Go to tab", steps, index=st.session_state.selected_tab, horizontal=True)
st.session_state.selected_tab = steps.index(sel)

if st.session_state.selected_tab == 0:
    st.header("Instructor Setup")
    st.session_state.true_price = st.number_input("Enter the True Stock Price (Keep hidden!)", value=st.session_state.get("true_price", 0.0), step=1.0)
    st.subheader("Mystery Asset Hints")
    st.session_state.hint1 = st.text_input("Sector", value=st.session_state.hint1, placeholder="e.g. Renewable Energy")
    st.session_state.hint2 = st.text_input("Revenue", value=st.session_state.hint2, placeholder="e.g. ~€12B")
    st.session_state.hint3 = st.text_input("Outstanding Shares", value=st.session_state.hint3, placeholder="e.g. ~420M")

elif st.session_state.selected_tab == 1:
    st.header("Compete for Market Maker")
    st.markdown("Students offer narrower and narrower range widths. Smallest width wins!")
    with st.form("bidding_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            bidder_name = st.text_input("Participant Name")
        with col2:
            range_width = st.number_input("Range Width", min_value=0.0, step=1.0)
        submit_bid = st.form_submit_button("Submit Range")
        if submit_bid and bidder_name:
            st.session_state.bids.append({"Name": bidder_name, "Range Width": range_width})
            st.success(f"{bidder_name} bid a width of {range_width}!")
    if st.session_state.bids:
        st.write("### Current Bids (Sorted by narrowest):")
        df_bids = pd.DataFrame(st.session_state.bids).sort_values(by="Range Width", ascending=True).reset_index(drop=True)
        st.dataframe(df_bids, use_container_width=True)
        st.session_state.winner = df_bids.iloc[0]["Name"]
        st.session_state.winning_width = df_bids.iloc[0]["Range Width"]
        st.info(f"The Market Maker is: **{st.session_state.winner}** with a width of **{st.session_state.winning_width}**!")
    else:
        st.session_state.winner = ""
        st.session_state.winning_width = 0.0

elif st.session_state.selected_tab == 2:
    st.header("Set the Market")
    if st.session_state.winner == "":
        st.warning("Please submit at least one bid in Tab 2 first.")
    else:
        st.markdown(f"**{st.session_state.winner}** must now set the Bid. The Ask is calculated automatically to maintain the **{st.session_state.winning_width}** width.")
        st.session_state.mm_name = st.text_input("Market Maker Name", value=st.session_state.winner)
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.bid = st.number_input("Bid (Lower Bound)", value=st.session_state.get("bid", 0.0), step=1.0)
        with col2:
            st.session_state.ask = st.session_state.bid + st.session_state.winning_width
            st.number_input("Ask (Upper Bound)", value=st.session_state.ask, disabled=True)
        st.success(f"Market established: **{st.session_state.bid}** (Bid) / **{st.session_state.ask}** (Ask)")

elif st.session_state.selected_tab == 3:
    st.header("Traders")
    with st.form("trade_form", clear_on_submit=True):
        trader_name = st.text_input("Trader Name")
        action = st.radio("Action", ["Buy at Ask (Bet Over)", "Sell at Bid (Bet Under)"])
        submit_trade = st.form_submit_button("Add Trade")
        if submit_trade and trader_name:
            st.session_state.trades.append({"Name": trader_name, "Action": action})
            st.success(f"Trade added for {trader_name}!")
    if st.session_state.trades:
        st.write("### Current Order Book:")
        st.dataframe(pd.DataFrame(st.session_state.trades), use_container_width=True)

elif st.session_state.selected_tab == 4:
    st.header("Resolve the Market")
    if st.button("Reveal Price & Calculate Payouts", type="primary"):
        st.subheader(f"The True Price is: **${st.session_state.get('true_price', 0.0)}**")
        st.write(f"Spread: Bid = ${st.session_state.get('bid', 0.0)}, Ask = ${st.session_state.get('ask', 0.0)}")
        mm_profit = 0
        results = []
        current_bid = st.session_state.get("bid", 0.0)
        current_ask = st.session_state.get("ask", 0.0)
        mm_name = st.session_state.get("mm_name", "Market Maker")
        for trade in st.session_state.trades:
            is_buyer = "Buy" in trade["Action"]
            true_price = st.session_state.get('true_price', 0.0)

            if is_buyer:
                trader_profit = true_price - current_ask
            else:
                trader_profit = current_bid - true_price

            mm_profit -= trader_profit
            results.append({"Trader": trade["Name"], "Action": trade["Action"], "P&L": trader_profit})
        st.divider()
        st.write(f"### Market Maker ({mm_name}) Total P&L: **${mm_profit:.2f}**")
        st.write("### Trader Results:")
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.write("No trades were placed.")

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("Previous"):
        st.session_state.selected_tab = max(0, st.session_state.selected_tab - 1)
        st.rerun()
with col2:
    st.write(f"**Current tab:** {steps[st.session_state.selected_tab]}")
with col3:
    if st.button("Next"):
        st.session_state.selected_tab = min(len(steps) - 1, st.session_state.selected_tab + 1)
        st.rerun()