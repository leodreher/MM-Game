import streamlit as st
import pandas as pd

# Initialize session state
if 'trades' not in st.session_state:
    st.session_state.trades = []
if 'bids' not in st.session_state:
    st.session_state.bids = []

st.title("Market Maker Game 📈")

# Sustainable Finance Context
st.markdown("**Mystery Asset:** A leading offshore wind energy company.")
st.markdown("*Hints:* Sector: Renewable Energy | Revenue: ~€12B | Shares: ~420M")
st.divider()

# 5 Tabs now
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
        # Sort dataframe so smallest width is at the top
        df_bids = pd.DataFrame(st.session_state.bids).sort_values(by="Range Width", ascending=True).reset_index(drop=True)
        st.dataframe(df_bids, use_container_width=True)
        
        winner = df_bids.iloc[0]["Name"]
        winning_width = df_bids.iloc[0]["Range Width"]
        st.info(f"🏆 Current Winner: **{winner}** with a width of **{winning_width}**!")

with tab3:
    st.header("Set the Market")
    st.markdown("The winning Market Maker now sets the exact bounds.")
    
    # Auto-fill the winner's name if there are bids
    default_mm = winner if st.session_state.bids else ""
    mm_name = st.text_input("Market Maker Name", value=default_mm)
    
    col1, col2 = st.columns(2)
    with col1:
        bid = st.number_input("Final Bid (Lower Bound)", value=0.0, step=1.0)
    with col2:
        ask = st.number_input("Final Ask (Upper Bound)", value=0.0, step=1.0)
        
    if ask - bid > 0:
        st.caption(f"Current Spread: {ask - bid}")

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

        for trade in st.session_state.trades:
            trader_profit = 0
            is_buyer = "Buy" in trade["Action"]

            if true_price > ask:  # Buyers win
                if is_buyer:
                    trader_profit = true_price - ask
                    mm_profit -= trader_profit
            elif true_price < bid:  # Sellers win
                if not is_buyer:
                    trader_profit = bid - true_price
                    mm_profit -= trader_profit
            else:  # Market Maker Wins (Bid <= Price <= Ask)
                if is_buyer:
                    trader_loss = ask - true_price
                    mm_profit += trader_loss
                    trader_profit = -trader_loss
                else:
                    trader_loss = true_price - bid
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