import streamlit as st
import pandas as pd

# Initialize session state
if 'trades' not in st.session_state:
    st.session_state.trades = []
if 'bids' not in st.session_state:
    st.session_state.bids = []

st.title("Market Making Game 📈")

# Sustainable Finance Context
st.markdown("**Mystery Asset:** A leading offshore wind energy company.")
st.markdown("*Hints:* Sector: Renewable Energy | Revenue: ~€12B | Shares: ~420M")
st.divider()

# 5 Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["1. Setup", "2. Bidding", "3. Market Maker", "4. Trading", "5. Resolution"])

with tab1:
    st.header("Instructor Setup")
    true_price = st.number_input("Enter the True Stock Price (Keep hidden!)", value=0.0, step=1.0)

with tab2:
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
        
        winner = df_bids.iloc[0]["Name"]
        winning_width = df_bids.iloc[0]["Range Width"]
        st.info(f"The Market Maker is: **{winner}** with a width of **{winning_width}**!")
    else:
        winner = ""
        winning_width = 0.0

with tab3:
    st.header("Set the Market")
    if winner == "":
        st.warning("Please submit at least one bid in Tab 2 first.")
    else:
        st.markdown(f"**{winner}** must now set the Bid. The Ask is calculated automatically to maintain the **{winning_width}** width.")
        
        mm_name = st.text_input("Market Maker Name", value=winner)
        
        col1, col2 = st.columns(2)
        with col1:
            bid = st.number_input("Bid (Lower Bound)", value=0.0, step=1.0)
        with col2:
            # Enforce the width by calculating Ask based on Bid + winning_width
            ask = bid + winning_width
            st.number_input("Ask (Upper Bound)", value=ask, disabled=True)
            
        st.success(f"Market established: **{bid}** (Bid) / **{ask}** (Ask)")

with tab4:
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

with tab5:
    st.header("Resolve the Market")
    if st.button("Reveal Price & Calculate Payouts", type="primary"):
        st.subheader(f"The True Price is: **${true_price}**")
        
        mm_profit = 0
        results = []

        # We use the bid/ask from the current state of Tab 3
        # Since Tab 3 UI elements define 'bid' and 'ask' locally, 
        # we need to ensure they are calculated here too.
        current_bid = bid
        current_ask = ask

        for trade in st.session_state.trades:
            trader_profit = 0
            is_buyer = "Buy" in trade["Action"]

            if true_price > current_ask:  # Buyers win
                if is_buyer:
                    trader_profit = true_price - current_ask
                    mm_profit -= trader_profit
            elif true_price < current_bid:  # Sellers win
                if not is_buyer:
                    trader_profit = current_bid - true_price
                    mm_profit -= trader_profit
            else:  # Market Maker Wins (Bid <= Price <= Ask)
                if is_buyer:
                    trader_loss = current_ask - true_price
                    mm_profit += trader_loss
                    trader_profit = -trader_loss
                else:
                    trader_loss = true_price - current_bid
                    mm_profit += trader_loss
                    trader_profit = -trader_loss

            results.append({"Trader": trade["Name"], "Action": trade["Action"], "P&L": trader_profit})

        st.divider()
        st.write(f"### Market Maker ({mm_name}) Total P&L: **${mm_profit:.2f}**")
        st.write("### Trader Results:")
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.write("No trades were placed.")