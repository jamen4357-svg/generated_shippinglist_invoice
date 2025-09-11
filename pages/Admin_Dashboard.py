import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from login import (
    get_security_stats, log_security_event, log_business_activity,
    get_business_activities, get_activity_summary,
    create_user, generate_registration_token, USER_DB_PATH
)
from auth_wrapper import setup_page_auth, create_admin_check_decorator

# --- Enhanced Admin Authentication Setup ---
user_info = setup_page_auth(
    page_title="Admin Dashboard", 
    page_name="Admin Dashboard",
    admin_required=True,
    layout="wide"
)

st.title("🛡️ Admin Dashboard")
st.info("Comprehensive system monitoring, security, and storage management.")

# --- Tab Navigation ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview", 
    "🔒 Security Monitor", 
    "📋 Activity Monitor", 
    "💾 Storage Manager",
    "👥 User Management",
    "🔑 Token Management"
])

# --- Tab 1: Overview ---
with tab1:
    st.header("📊 System Overview")
    
    # Get all statistics
    try:
        security_stats = get_security_stats()
        # Note: business_activities and storage_stats functions are no longer available
        # after session system removal for security reasons
        
        # System health metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Security health
            if security_stats:
                failed_logins = security_stats.get('failed_logins_24h', 0)
                locked_accounts = security_stats.get('locked_accounts', 0)
                total_users = security_stats.get('total_users', 0)
                
                # Calculate security score based on failed logins and locked accounts
                security_score = max(0, 100 - (failed_logins * 5) - (locked_accounts * 10))
                
                if security_score >= 80:
                    st.success(f"🔒 Security: {security_score}/100")
                elif security_score >= 60:
                    st.warning(f"🔒 Security: {security_score}/100")
                else:
                    st.error(f"🔒 Security: {security_score}/100")
                
                st.caption(f"Users: {total_users} | Failed: {failed_logins} | Locked: {locked_accounts}")
            else:
                st.info("🔒 Security: No data")
        
        with col2:
            # Activity health
            try:
                activity_summary = get_activity_summary(days_back=1)
                today_activities = activity_summary['total_activities']
                success_rate = activity_summary['success_rate']
                
                if today_activities > 0:
                    if success_rate >= 90:
                        st.success(f"📋 Activity: {today_activities} today")
                    elif success_rate >= 70:
                        st.warning(f"📋 Activity: {today_activities} today")
                    else:
                        st.error(f"📋 Activity: {today_activities} today")
                    st.caption(f"Success Rate: {success_rate}%")
                else:
                    st.info("📋 Activity: No activity today")
            except:
                st.info("📋 Activity: Data unavailable")
        
        with col3:
            # Storage health
            st.info("💾 Storage: Storage monitoring removed for security")
            st.caption("Storage tracking disabled after session system removal")
        
        with col4:
            # Overall system health
            if security_stats:
                try:
                    activity_summary = get_activity_summary(days_back=1)
                    today_activities = activity_summary['total_activities']
                    success_rate = activity_summary['success_rate']
                    
                    # Calculate overall score including activity metrics
                    overall_score = security_score
                    
                    # Adjust score based on activity success rate
                    if today_activities > 0:
                        if success_rate >= 90:
                            overall_score += 10
                        elif success_rate >= 70:
                            overall_score += 5
                        else:
                            overall_score -= 10
                    
                    # Cap score at 100
                    overall_score = min(100, max(0, overall_score))
                    
                    if overall_score >= 80:
                        st.success(f"🏥 Overall: {overall_score}/100")
                    elif overall_score >= 60:
                        st.warning(f"🏥 Overall: {overall_score}/100")
                    else:
                        st.error(f"🏥 Overall: {overall_score}/100")
                    
                    if today_activities > 0:
                        st.caption(f"Security: {security_score} | Activity: {success_rate}%")
                    else:
                        st.caption("Based on security metrics only")
                except:
                    overall_score = security_score
                    if overall_score >= 80:
                        st.success(f"🏥 Overall: {overall_score}/100")
                    elif overall_score >= 60:
                        st.warning(f"🏥 Overall: {overall_score}/100")
                    else:
                        st.error(f"🏥 Overall: {overall_score}/100")
                    st.caption("Based on security metrics only")
            else:
                st.info("🏥 Overall: No data")
        
        # Recent activity summary
        st.subheader("📈 Recent Activity Summary")
        
        try:
            # Get recent activities for summary
            recent_activities = get_business_activities(limit=10, days_back=1)
            
            if recent_activities:
                st.success(f"✅ **{len(recent_activities)} activities recorded today**")
                
                # Show recent activity types
                activity_types = {}
                for activity in recent_activities:
                    activity_type = activity['activity_type']
                    activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
                
                if activity_types:
                    st.write("**Today's Activity Breakdown:**")
                    for activity_type, count in activity_types.items():
                        st.write(f"• {activity_type}: {count}")
                
                # Show most recent activity
                if recent_activities:
                    latest = recent_activities[0]
                    st.info(f"**Latest Activity:** {latest['username']} performed {latest['activity_type']} at {latest['timestamp']}")
            else:
                st.info("ℹ️ **No activities recorded today**")
                st.caption("System is quiet - no business activities logged.")
                
        except Exception as e:
            st.info("ℹ️ **Note:** Activity tracking is available but data loading failed.")
            st.caption(f"Error: {e}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("🔒 **Security Status**")
            if security_stats:
                st.write(f"• Failed logins (24h): {security_stats.get('failed_logins_24h', 0)}")
                st.write(f"• Locked accounts: {security_stats.get('locked_accounts', 0)}")
                st.write(f"• Total users: {security_stats.get('total_users', 0)}")
            else:
                st.write("• No security data available")
        
        with col2:
            st.info("📋 **System Status**")
            st.write("• Activity monitoring: ✅ Active")
            st.write("• Session tracking: 🔒 Removed")
            st.write("• Enhanced security: ✅ Active")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        st.info("ℹ️ **Note:** Advanced system management features have been simplified for enhanced security.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Data", key="refresh_all_data"):
                st.rerun()
        
        with col2:
            st.info("🧹 **Cleanup Status**")
            st.write("• Advanced cleanup: 🔒 Disabled")
            st.write("• Enhanced security: ✅ Active")
        
        with col3:
            st.info("⚡ **Optimization Status**")
            st.write("• Database optimization: 🔒 Disabled")
            st.write("• Enhanced security: ✅ Active")
        
    except Exception as e:
        st.error(f"Error loading overview data: {e}")

# --- Tab 2: Security Monitor ---
with tab2:
    st.header("🔒 Security Monitor")
    st.info("Real-time security monitoring and threat detection")
    
    # Get security statistics first
    try:
        security_stats = get_security_stats()
        
        if security_stats:
            # Enhanced Security Dashboard
            st.subheader("📊 Security Overview")
            
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                failed_logins = security_stats.get('failed_logins_24h', 0)
                st.metric("Failed Logins (24h)", failed_logins)
            
            with col2:
                locked_accounts = security_stats.get('locked_accounts', 0)
                st.metric("Locked Accounts", locked_accounts)
            
            with col3:
                total_users = security_stats.get('total_users', 0)
                st.metric("Total Users", total_users)
            
            with col4:
                # Get failed logins in last hour
                import sqlite3
                conn = sqlite3.connect(USER_DB_PATH)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM security_events 
                    WHERE event_type = 'LOGIN_FAILED' 
                    AND timestamp > datetime('now', '-1 hour')
                ''')
                failed_1h = cursor.fetchone()[0]
                conn.close()
                st.metric("Failed (1h)", failed_1h, delta=f"+{failed_1h}")
            
            with col5:
                # Get active tokens
                conn = sqlite3.connect(USER_DB_PATH)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM registration_tokens 
                    WHERE is_active = 1 AND expires_at > datetime('now')
                ''')
                active_tokens = cursor.fetchone()[0]
                conn.close()
                st.metric("Active Tokens", active_tokens)
            
            with col6:
                # Security status indicator
                security_score = max(0, 100 - (failed_logins * 5) - (locked_accounts * 10))
                if security_score >= 80:
                    st.success("🟢 Secure")
                elif security_score >= 60:
                    st.warning("🟡 Monitor")
                else:
                    st.error("🔴 Alert")
                st.caption(f"Score: {security_score}/100")
            
            st.markdown("---")
            
            # Security Charts and Analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Failed Login Trends (7 Days)")
                try:
                    conn = sqlite3.connect(USER_DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT date(timestamp) as date, COUNT(*) as count
                        FROM security_events 
                        WHERE event_type = 'LOGIN_FAILED' 
                        AND timestamp > datetime('now', '-7 days')
                        GROUP BY date(timestamp)
                        ORDER BY date
                    ''')
                    trends_data = cursor.fetchall()
                    conn.close()
                    
                    if trends_data:
                        trends_df = pd.DataFrame(trends_data, columns=['Date', 'Failed Logins'])
                        trends_df['Date'] = pd.to_datetime(trends_df['Date'])
                        fig = px.line(trends_df, x='Date', y='Failed Logins', 
                                     title="Daily Failed Login Attempts")
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No failed login data for the last 7 days")
                except Exception as e:
                    st.error(f"Error loading trends: {e}")
            
            with col2:
                st.subheader("🚨 Suspicious Activities")
                try:
                    conn = sqlite3.connect(USER_DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT ip_address, COUNT(*) as failed_attempts,
                               MAX(timestamp) as last_attempt
                        FROM security_events 
                        WHERE event_type = 'LOGIN_FAILED' 
                        AND timestamp > datetime('now', '-24 hours')
                        AND ip_address IS NOT NULL
                        GROUP BY ip_address
                        HAVING COUNT(*) >= 3
                        ORDER BY failed_attempts DESC
                    ''')
                    suspicious_data = cursor.fetchall()
                    conn.close()
                    
                    if suspicious_data:
                        suspicious_df = pd.DataFrame(suspicious_data, columns=[
                            'IP Address', 'Failed Attempts', 'Last Attempt'
                        ])
                        suspicious_df['Last Attempt'] = pd.to_datetime(suspicious_df['Last Attempt'])
                        st.dataframe(suspicious_df, use_container_width=True, hide_index=True)
                    else:
                        st.success("No suspicious activities detected")
                except Exception as e:
                    st.error(f"Error loading suspicious activities: {e}")
            
            st.markdown("---")
            
            # Recent Security Events
            st.subheader("📋 Recent Security Events")
            
            # Event filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                event_limit = st.selectbox("Show events", [25, 50, 100], index=1, key="security_event_limit")
            
            with col2:
                event_types = ['All', 'LOGIN_FAILED', 'LOGIN_SUCCESS', 'LOGOUT', 'ACCOUNT_LOCKED']
                selected_type = st.selectbox("Event type", event_types, key="security_event_type")
            
            with col3:
                if st.button("🔄 Refresh Events", key="refresh_security_events"):
                    st.rerun()
            
            # Get and display events
            try:
                conn = sqlite3.connect(USER_DB_PATH)
                cursor = conn.cursor()
                
                if selected_type == 'All':
                    cursor.execute('''
                        SELECT se.timestamp, se.event_type, se.description, 
                               u.username, se.ip_address
                        FROM security_events se
                        LEFT JOIN users u ON se.user_id = u.id
                        ORDER BY se.timestamp DESC
                        LIMIT ?
                    ''', (event_limit,))
                else:
                    cursor.execute('''
                        SELECT se.timestamp, se.event_type, se.description, 
                               u.username, se.ip_address
                        FROM security_events se
                        LEFT JOIN users u ON se.user_id = u.id
                        WHERE se.event_type = ?
                        ORDER BY se.timestamp DESC
                        LIMIT ?
                    ''', (selected_type, event_limit))
                
                events = cursor.fetchall()
                conn.close()
                
                if events:
                    events_df = pd.DataFrame(events, columns=[
                        'Timestamp', 'Event Type', 'Description', 'Username', 'IP Address'
                    ])
                    events_df['Timestamp'] = pd.to_datetime(events_df['Timestamp'])
                    
                    # Color code the dataframe
                    def highlight_events(row):
                        if row['Event Type'] == 'LOGIN_FAILED':
                            return ['background-color: #ffebee'] * len(row)
                        elif row['Event Type'] == 'ACCOUNT_LOCKED':
                            return ['background-color: #ffcdd2'] * len(row)
                        elif row['Event Type'] == 'LOGIN_SUCCESS':
                            return ['background-color: #e8f5e8'] * len(row)
                        else:
                            return [''] * len(row)
                    
                    styled_df = events_df.style.apply(highlight_events, axis=1)
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)
                    
                    # Export option
                    csv = events_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Security Log (CSV)",
                        data=csv,
                        file_name=f"security_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No security events found")
                    
            except Exception as e:
                st.error(f"Error loading security events: {e}")
            
            st.markdown("---")
            
            # Security Actions
            st.subheader("🛡️ Security Actions")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔓 Unlock All Accounts", key="unlock_all_accounts"):
                    try:
                        conn = sqlite3.connect(USER_DB_PATH)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE users SET locked_until = NULL WHERE locked_until > datetime('now')")
                        affected = cursor.rowcount
                        conn.commit()
                        conn.close()
                        
                        if affected > 0:
                            st.success(f"✅ Unlocked {affected} accounts")
                            log_security_event(user_info['user_id'], 'ADMIN_ACTION', 
                                             f'Admin unlocked {affected} accounts')
                            st.rerun()
                        else:
                            st.info("No locked accounts found")
                    except Exception as e:
                        st.error(f"Error unlocking accounts: {e}")
            
            with col2:
                if st.button("🗑️ Clear Old Events", key="clear_old_events"):
                    try:
                        conn = sqlite3.connect(USER_DB_PATH)
                        cursor = conn.cursor()
                        cursor.execute('''
                            DELETE FROM security_events 
                            WHERE timestamp < datetime('now', '-30 days')
                        ''')
                        affected = cursor.rowcount
                        conn.commit()
                        conn.close()
                        
                        if affected > 0:
                            st.success(f"✅ Cleared {affected} old events")
                            log_security_event(user_info['user_id'], 'ADMIN_ACTION', 
                                             f'Admin cleared {affected} old security events')
                            st.rerun()
                        else:
                            st.info("No old events to clear")
                    except Exception as e:
                        st.error(f"Error clearing events: {e}")
            
            with col3:
                # Security status summary
                st.info("🔒 **Security Status**")
                if failed_logins == 0 and locked_accounts == 0:
                    st.success("System is secure")
                elif failed_logins < 5:
                    st.warning("Monitor activity")
                else:
                    st.error("High alert")
            
            # Auto-refresh option
            st.markdown("---")
            if st.checkbox("🔄 Auto-refresh (30 seconds)", key="security_auto_refresh"):
                import time
                time.sleep(30)
                st.rerun()
            
        else:
            st.info("No security statistics available.")
            
    except Exception as e:
        st.error(f"Error loading security data: {e}")

# --- Tab 3: Activity Monitor ---
with tab3:
    st.header("📋 Activity Monitor")
    st.info("Track business activities, data verification, and invoice operations.")
    
    # Activity filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        activity_type_filter = st.selectbox(
            "Filter by Activity Type",
            ["All", "DATA_VERIFICATION", "DATA_AMENDMENT", "INVOICE_EDIT", "INVOICE_VOID", "INVOICE_REACTIVATE", "INVOICE_DELETE", "USER_CREATED", "TEMPLATE_ANALYSIS", "TEMPLATE_CREATED", "MAPPING_UPDATED"],
            key="activity_type_filter"
        )
    
    with col2:
        username_filter = st.text_input("Filter by Username", "", key="activity_username_filter")
    
    with col3:
        invoice_no_filter = st.text_input("Filter by Invoice No", "", key="activity_invoice_filter")
    
    with col4:
        activity_days_filter = st.number_input(
            "Days to look back",
            min_value=1,
            max_value=90,
            value=7,
            key="activity_days_filter"
        )
    
    # Get activity data
    try:
        activities = get_business_activities(
            limit=100,
            days_back=activity_days_filter,
            activity_type=activity_type_filter if activity_type_filter != "All" else None,
            username=username_filter if username_filter else None,
            invoice_ref=invoice_no_filter if invoice_no_filter else None
        )
        
        # Get activity summary
        summary = get_activity_summary(days_back=activity_days_filter)
        
        # Activity Summary Cards
        st.subheader("📊 Activity Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Activities", summary['total_activities'])
        
        with col2:
            st.metric("Success Rate", f"{summary['success_rate']}%")
        
        with col3:
            if summary['activities_by_type']:
                most_common_type = max(summary['activities_by_type'].items(), key=lambda x: x[1])
                st.metric("Most Common Activity", f"{most_common_type[0]}")
            else:
                st.metric("Most Common Activity", "N/A")
        
        with col4:
            if summary['activities_by_user']:
                most_active_user = max(summary['activities_by_user'].items(), key=lambda x: x[1])
                st.metric("Most Active User", f"{most_active_user[0]}")
            else:
                st.metric("Most Active User", "N/A")
        
        # Activity Charts
        if summary['activities_by_type']:
            st.subheader("📈 Activity Distribution")
            col1, col2 = st.columns(2)
            
            with col1:
                # Activity by type chart
                activity_df = pd.DataFrame(list(summary['activities_by_type'].items()), 
                                         columns=['Activity Type', 'Count'])
                fig = px.pie(activity_df, values='Count', names='Activity Type', 
                            title="Activities by Type")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Activity by user chart
                if summary['activities_by_user']:
                    user_df = pd.DataFrame(list(summary['activities_by_user'].items()), 
                                         columns=['Username', 'Count'])
                    fig = px.bar(user_df, x='Username', y='Count', 
                                title="Activities by User")
                    st.plotly_chart(fig, use_container_width=True)
        
        # Activity Details Table
        st.subheader("📋 Recent Activity Details")
        
        if activities:
            # Prepare data for display
            display_data = []
            for activity in activities:
                display_data.append({
                    'Timestamp': activity['timestamp'],
                    'User': activity['username'],
                    'Activity': activity['activity_type'],
                    'Invoice Ref': activity['target_invoice_ref'] or 'N/A',
                    'Invoice No': activity['target_invoice_no'] or 'N/A',
                    'Description': activity['action_description'] or 'N/A',
                    'Success': '✅' if activity['success'] else '❌',
                    'IP': activity['ip_address'] or 'N/A'
                })
            
            # Create DataFrame and display
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Export option
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Activity Data (CSV)",
                data=csv,
                file_name=f"activity_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
        else:
            st.info("No activities found for the selected filters.")
            
    except Exception as e:
        st.error(f"Error loading activity data: {e}")
        st.info("Activity monitoring may be temporarily unavailable.")

# --- Tab 4: Storage Manager ---
with tab4:
    st.header("💾 Storage Manager")
    st.info("Monitor and manage database storage, cleanup old data, and optimize performance.")
    
    # Storage monitoring
    st.info("ℹ️ **Note:** Detailed storage monitoring has been removed for enhanced security after session system removal.")
    st.caption("Storage tracking is disabled to prevent potential security vulnerabilities.")
    
    # Basic storage info
    st.subheader("📊 Basic Storage Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("🔒 **Security Status**")
        st.write("• Storage monitoring disabled")
        st.write("• Session-based tracking removed")
        st.write("• Enhanced security measures active")
    
    with col2:
        st.info("📋 **Future Plans**")
        st.write("• Secure storage analytics")
        st.write("• Privacy-preserving metrics")
        st.write("• Compliance-focused monitoring")
    
    # Placeholder for future implementation
    st.subheader("💡 Storage Recommendations")
    st.info("Storage monitoring will be re-implemented with enhanced security measures in future updates.")

# --- Tab 5: User Management ---
with tab5:
    st.header("👥 User Management")
    st.info("Manage users, their permissions, and account status.")
    
    # User Management Tabs
    user_tab1, user_tab2, user_tab3 = st.tabs(["📋 User List", "➕ Create New User", "🔧 User Actions"])
    
    with user_tab1:
        st.subheader("📋 Current Users")
        
        # User filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            role_filter = st.selectbox("Filter by Role", ["All", "admin", "user"], key="user_list_role_filter")
        
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive", "Locked"], key="user_list_status_filter")
        
        with col3:
            if st.button("🔄 Refresh Users", key="refresh_users_list"):
                st.rerun()
        
        # Get and display users
        try:
            conn = sqlite3.connect(USER_DB_PATH)
            cursor = conn.cursor()
            
            # Build query based on filters
            query = '''
                SELECT id, username, role, is_active, created_at, last_login, 
                       failed_attempts, locked_until
                FROM users
                WHERE 1=1
            '''
            params = []
            
            if role_filter != "All":
                query += " AND role = ?"
                params.append(role_filter)
            
            if status_filter == "Active":
                query += " AND is_active = 1 AND (locked_until IS NULL OR locked_until <= datetime('now'))"
            elif status_filter == "Inactive":
                query += " AND is_active = 0"
            elif status_filter == "Locked":
                query += " AND locked_until > datetime('now')"
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            users = cursor.fetchall()
            conn.close()
            
            if users:
                # Display user statistics
                st.subheader("📊 User Statistics")
                col1, col2, col3, col4 = st.columns(4)
                
                total_users = len(users)
                active_users = len([u for u in users if u[3] == 1])  # is_active
                locked_users = len([u for u in users if u[7] and u[7] > datetime.now().isoformat()])  # locked_until
                admin_users = len([u for u in users if u[2] == 'admin'])  # role
                
                with col1:
                    st.metric("Total Users", total_users)
                
                with col2:
                    st.metric("Active Users", active_users)
                
                with col3:
                    st.metric("Locked Users", locked_users)
                
                with col4:
                    st.metric("Admin Users", admin_users)
                
                # Display users table
                st.subheader("👥 User Details")
                
                # Prepare data for display
                display_data = []
                for user in users:
                    user_id, username, role, is_active, created_at, last_login, failed_attempts, locked_until = user
                    
                    # Determine status
                    if locked_until and locked_until > datetime.now().isoformat():
                        status = "🔒 Locked"
                        status_color = "🔴"
                    elif is_active:
                        status = "✅ Active"
                        status_color = "🟢"
                    else:
                        status = "❌ Inactive"
                        status_color = "🟡"
                    
                    display_data.append({
                        'ID': user_id,
                        'Username': username,
                        'Role': role.title(),
                        'Status': status,
                        'Created': created_at[:19] if created_at else 'N/A',
                        'Last Login': last_login[:19] if last_login else 'Never',
                        'Failed Attempts': failed_attempts or 0,
                        'Locked Until': locked_until[:19] if locked_until else 'N/A'
                    })
                
                # Create DataFrame and display
                df = pd.DataFrame(display_data)
                
                # Color code the dataframe based on status
                def highlight_users(row):
                    if '🔒 Locked' in row['Status']:
                        return ['background-color: #ffcdd2'] * len(row)
                    elif '❌ Inactive' in row['Status']:
                        return ['background-color: #fff3e0'] * len(row)
                    elif 'admin' in row['Role'].lower():
                        return ['background-color: #e3f2fd'] * len(row)
                    else:
                        return [''] * len(row)
                
                styled_df = df.style.apply(highlight_users, axis=1)
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
                
                # Export option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download User List (CSV)",
                    data=csv,
                    file_name=f"user_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
            else:
                st.info("No users found matching the selected filters.")
                
        except Exception as e:
            st.error(f"Error loading users: {e}")
    
    with user_tab2:
        st.subheader("➕ Create New User")
        
        # User creation form
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username", help="Enter a unique username", key="create_username")
                password = st.text_input("Password", type="password", help="Enter a secure password", key="create_password")
                confirm_password = st.text_input("Confirm Password", type="password", help="Confirm the password", key="create_confirm_password")
            
            with col2:
                role = st.selectbox("Role", ["user", "admin"], help="Select user role", key="create_user_role")
                is_active = st.checkbox("Active User", value=True, help="User can log in", key="create_user_active")
                
                st.info("**Password Requirements:**")
                st.write("• Minimum 6 characters")
                st.write("• Recommended: Mix of letters, numbers, symbols")
            
            if st.form_submit_button("Create User"):
                if username and password and confirm_password:
                    if password != confirm_password:
                        st.error("❌ Passwords do not match!")
                    elif len(password) < 6:
                        st.error("❌ Password must be at least 6 characters long!")
                    else:
                        try:
                            # Create user using available function
                            success, message = create_user(username, password, role)
                            if success:
                                st.success(f"✅ User '{username}' created successfully!")
                                st.info("User can now log in with the provided credentials.")
                                
                                # Log the user creation
                                log_security_event(user_info['user_id'], 'USER_CREATED', 
                                                 f'Admin created new user: {username} with role: {role}')
                                
                                # Show user details
                                st.subheader("👤 New User Details")
                                st.write(f"**Username:** {username}")
                                st.write(f"**Role:** {role.title()}")
                                st.write(f"**Status:** {'Active' if is_active else 'Inactive'}")
                                st.write(f"**Created by:** {user_info['username']}")
                                
                            else:
                                st.error(f"❌ Error creating user: {message}")
                        except Exception as e:
                            st.error(f"❌ Error creating user: {e}")
                else:
                    st.error("Please fill in all required fields.")
    
    with user_tab3:
        st.subheader("🔧 User Actions")
        st.info("Perform administrative actions on user accounts.")
        
        # User search and selection
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_username = st.text_input("🔍 Search Username", placeholder="Type username to search...", key="user_search_username")
        
        with col2:
            search_role = st.selectbox("Filter by Role", ["All", "admin", "user"], key="user_search_role_filter")
        
        with col3:
            search_status = st.selectbox("Filter by Status", ["All", "Active", "Inactive", "Locked"], key="user_search_status_filter")
        
        # Search and display matching users
        if search_username:
            try:
                conn = sqlite3.connect(USER_DB_PATH)
                cursor = conn.cursor()
                
                # Build search query
                query = '''
                    SELECT id, username, role, is_active, locked_until, failed_attempts, created_at, last_login
                    FROM users 
                    WHERE username LIKE ?
                '''
                params = [f"%{search_username}%"]
                
                if search_role != "All":
                    query += " AND role = ?"
                    params.append(search_role)
                
                if search_status == "Active":
                    query += " AND is_active = 1 AND (locked_until IS NULL OR locked_until <= datetime('now'))"
                elif search_status == "Inactive":
                    query += " AND is_active = 0"
                elif search_status == "Locked":
                    query += " AND locked_until > datetime('now')"
                
                query += " ORDER BY username LIMIT 20"  # Limit results for performance
                
                cursor.execute(query, params)
                matching_users = cursor.fetchall()
                conn.close()
                
                if matching_users:
                    st.subheader(f"🔍 Search Results ({len(matching_users)} found)")
                    
                    # Display matching users as cards for easy selection
                    for user in matching_users:
                        user_id, username, role, is_active, locked_until, failed_attempts, created_at, last_login = user
                        
                        # Determine status
                        if locked_until and locked_until > datetime.now().isoformat():
                            status_icon = "🔒"
                            status_text = "Locked"
                            status_color = "red"
                        elif is_active:
                            status_icon = "✅"
                            status_text = "Active"
                            status_color = "green"
                        else:
                            status_icon = "❌"
                            status_text = "Inactive"
                            status_color = "orange"
                        
                        # Create expandable user card
                        with st.expander(f"{status_icon} {username} ({role}) - {status_text}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**User ID:** {user_id}")
                                st.write(f"**Username:** {username}")
                                st.write(f"**Role:** {role.title()}")
                                st.write(f"**Status:** {status_text}")
                                st.write(f"**Failed Attempts:** {failed_attempts or 0}")
                            
                            with col2:
                                st.write(f"**Created:** {created_at[:19] if created_at else 'N/A'}")
                                st.write(f"**Last Login:** {last_login[:19] if last_login else 'Never'}")
                                if locked_until and locked_until > datetime.now().isoformat():
                                    st.write(f"**Locked Until:** {locked_until[:19]}")
                                else:
                                    st.write("**Locked Until:** Not locked")
                            
                            # Action buttons for this specific user
                            st.markdown("**Actions:**")
                            action_col1, action_col2, action_col3, action_col4 = st.columns(4)
                            
                            with action_col1:
                                if st.button(f"🔓 Unlock", key=f"unlock_{user_id}"):
                                    try:
                                        conn = sqlite3.connect(USER_DB_PATH)
                                        cursor = conn.cursor()
                                        cursor.execute('''
                                            UPDATE users 
                                            SET locked_until = NULL, failed_attempts = 0 
                                            WHERE id = ?
                                        ''', (user_id,))
                                        conn.commit()
                                        conn.close()
                                        
                                        st.success(f"✅ User '{username}' unlocked!")
                                        log_security_event(user_info['user_id'], 'ADMIN_ACTION', 
                                                         f'Admin unlocked user: {username}')
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {e}")
                            
                            with action_col2:
                                if is_active:
                                    if st.button(f"❌ Deactivate", key=f"deactivate_{user_id}"):
                                        if username == user_info['username']:
                                            st.error("❌ Cannot deactivate your own account!")
                                        else:
                                            try:
                                                conn = sqlite3.connect(USER_DB_PATH)
                                                cursor = conn.cursor()
                                                cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
                                                conn.commit()
                                                conn.close()
                                                
                                                st.success(f"✅ User '{username}' deactivated!")
                                                log_security_event(user_info['user_id'], 'ADMIN_ACTION', 
                                                                 f'Admin deactivated user: {username}')
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"Error: {e}")
                                else:
                                    if st.button(f"✅ Activate", key=f"activate_{user_id}"):
                                        try:
                                            conn = sqlite3.connect(USER_DB_PATH)
                                            cursor = conn.cursor()
                                            cursor.execute("UPDATE users SET is_active = 1 WHERE id = ?", (user_id,))
                                            conn.commit()
                                            conn.close()
                                            
                                            st.success(f"✅ User '{username}' activated!")
                                            log_security_event(user_info['user_id'], 'ADMIN_ACTION', 
                                                             f'Admin activated user: {username}')
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Error: {e}")
                            
                            with action_col3:
                                if st.button(f"🔄 Reset Attempts", key=f"reset_{user_id}"):
                                    try:
                                        conn = sqlite3.connect(USER_DB_PATH)
                                        cursor = conn.cursor()
                                        cursor.execute("UPDATE users SET failed_attempts = 0 WHERE id = ?", (user_id,))
                                        conn.commit()
                                        conn.close()
                                        
                                        st.success(f"✅ Reset failed attempts for '{username}'!")
                                        log_security_event(user_info['user_id'], 'ADMIN_ACTION', 
                                                         f'Admin reset failed attempts for user: {username}')
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {e}")
                            
                            with action_col4:
                                if role != 'admin':
                                    if st.button(f"⬆️ Make Admin", key=f"admin_{user_id}"):
                                        try:
                                            conn = sqlite3.connect(USER_DB_PATH)
                                            cursor = conn.cursor()
                                            cursor.execute("UPDATE users SET role = 'admin' WHERE id = ?", (user_id,))
                                            conn.commit()
                                            conn.close()
                                            
                                            st.success(f"✅ '{username}' is now an admin!")
                                            log_security_event(user_info['user_id'], 'ADMIN_ACTION', 
                                                             f'Admin promoted user to admin: {username}')
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Error: {e}")
                                else:
                                    if st.button(f"⬇️ Make User", key=f"user_{user_id}"):
                                        if username == user_info['username']:
                                            st.error("❌ Cannot demote yourself!")
                                        else:
                                            try:
                                                conn = sqlite3.connect(USER_DB_PATH)
                                                cursor = conn.cursor()
                                                cursor.execute("UPDATE users SET role = 'user' WHERE id = ?", (user_id,))
                                                conn.commit()
                                                conn.close()
                                                
                                                st.success(f"✅ '{username}' is now a regular user!")
                                                log_security_event(user_info['user_id'], 'ADMIN_ACTION', 
                                                                 f'Admin demoted admin to user: {username}')
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"Error: {e}")
                    
                    if len(matching_users) == 20:
                        st.info("ℹ️ Showing first 20 results. Refine your search for more specific results.")
                
                else:
                    st.info(f"No users found matching '{search_username}' with the selected filters.")
                    
            except Exception as e:
                st.error(f"Error searching users: {e}")
        
        else:
            st.info("👆 Enter a username in the search box above to find and manage specific users.")
            
            # Show some quick stats while waiting for search
            try:
                conn = sqlite3.connect(USER_DB_PATH)
                cursor = conn.cursor()
                
                # Quick stats
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
                active_users = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM users WHERE locked_until > datetime('now')")
                locked_users = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
                admin_users = cursor.fetchone()[0]
                
                conn.close()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Users", total_users)
                with col2:
                    st.metric("Active Users", active_users)
                with col3:
                    st.metric("Locked Users", locked_users)
                with col4:
                    st.metric("Admin Users", admin_users)
                    
            except Exception as e:
                st.error(f"Error loading stats: {e}")

# --- Tab 6: Token Management ---
with tab6:
    st.header("🔑 Registration Token Management")
    st.info("Generate and manage invitation tokens for user registration.")
    
    # Token Management Tabs
    token_tab1, token_tab2, token_tab3 = st.tabs(["🔑 Generate Tokens", "📋 Token List", "🧹 Token Cleanup"])
    
    with token_tab1:
        st.subheader("🔑 Generate New Registration Token")
        
        with st.form("generate_token_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                max_uses = st.number_input(
                    "Maximum Uses",
                    min_value=1,
                    max_value=10,
                    value=1,
                    help="How many times this token can be used",
                    key="token_max_uses"
                )
                
                expiry_days = st.number_input(
                    "Expiry Days",
                    min_value=1,
                    max_value=30,
                    value=7,
                    help="How many days until the token expires",
                    key="token_expiry_days"
                )
            
            with col2:
                st.write("**Token Settings:**")
                st.write(f"• Max uses: {max_uses}")
                st.write(f"• Expires in: {expiry_days} days")
                st.write(f"• Created by: {user_info['username']}")
            
            if st.form_submit_button("🔑 Generate Token"):
                with st.spinner("Generating token..."):
                    # Convert days to hours for the function
                    expires_hours = expiry_days * 24
                    try:
                        result = generate_registration_token(
                            user_info['user_id'], 
                            user_info['username'],
                            max_uses, 
                            expires_hours
                        )
                        success = result is not None
                    except Exception as e:
                        success = False
                        result = str(e)
                
                if success:
                    st.success("✅ Token generated successfully!")
                    
                    # Display the token
                    st.subheader("📋 Generated Token")
                    st.code(result, language="text")
                    
                    # Copy button
                    st.info("⚠️ **Important:** Copy this token now! It won't be shown again for security reasons.")
                    
                    # Token info
                    expiry_date = datetime.now() + timedelta(days=expiry_days)
                    st.write(f"**Token expires:** {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"**Registration URL:** `http://your-domain/register`")
                    
                else:
                    st.error(f"❌ Failed to generate token: {result}")
    
    with token_tab2:
        st.subheader("📋 All Registration Tokens")
        
        st.info("ℹ️ **Note:** Token listing has been simplified for enhanced security after session system removal.")
        st.caption("Token management features will be re-implemented with enhanced security measures in future updates.")
        
        # Placeholder for token list
        st.info("🔑 **Token Management Status**")
        st.write("• Token listing temporarily disabled")
        st.write("• Session-based token tracking removed")
        st.write("• Enhanced security measures active")
        
        # Show basic token info
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("📋 **Current Status**")
            st.write("• Token generation: ✅ Active")
            st.write("• Token validation: ✅ Active")
            st.write("• Token tracking: 🔒 Simplified")
        
        with col2:
            st.info("🔒 **Security Note**")
            st.write("• Token management simplified")
            st.write("• Enhanced security measures")
            st.write("• Future: Secure token analytics")
            # Token statistics placeholder
            st.info("📊 **Token Statistics**")
            st.write("• Detailed token analytics temporarily disabled")
            st.write("• Enhanced security measures active")
    
    with token_tab3:
        st.subheader("🧹 Token Cleanup")
        st.info("ℹ️ **Note:** Token cleanup has been simplified for enhanced security after session system removal.")
        st.caption("Token cleanup features will be re-implemented with enhanced security measures in future updates.")
        
        # Placeholder for token cleanup
        st.info("🔒 **Token Cleanup Status**")
        st.write("• Automatic cleanup: 🔒 Disabled")
        st.write("• Manual cleanup: 🔒 Disabled")
        st.write("• Enhanced security measures active")
        
        # Future plans
        st.subheader("💡 Future Implementation")
        st.write("• Secure token analytics")
        
        # Future plans
        st.subheader("💡 Future Implementation")
        st.write("• Secure token analytics")
        st.write("• Privacy-preserving cleanup")
        st.write("• Compliance-focused management")

# --- Footer ---
st.markdown("---")
st.markdown("*Admin Dashboard - Comprehensive system monitoring and management*")