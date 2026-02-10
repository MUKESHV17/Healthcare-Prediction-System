import { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';
import io from 'socket.io-client';

const socket = io('http://127.0.0.1:5001');

function NotificationBell({ email }) {
    const [notifications, setNotifications] = useState([]);
    const [isOpen, setIsOpen] = useState(false);

    useEffect(() => {
        if (email) {
            // Fetch initial
            fetch(`http://127.0.0.1:5001/notifications?email=${email}`)
                .then(res => res.json())
                .then(data => setNotifications(data))
                .catch(err => console.error(err));

            socket.on('notification', (data) => {
                if (data.email === email) {
                    setNotifications(prev => [data, ...prev]);
                }
            });
        }
        return () => {
            socket.off('notification');
        };
    }, [email]);

    const clearNotifications = async () => {
        setNotifications([]);
        await fetch("http://127.0.0.1:5001/notifications/clear", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email })
        });
    };

    const unreadCount = notifications.length;

    return (
        <div style={{ position: 'relative' }}>
            <div
                style={{ cursor: 'pointer', position: 'relative' }}
                onClick={() => setIsOpen(!isOpen)}
            >
                <Bell size={24} color="#555" />
                {unreadCount > 0 && (
                    <span style={{
                        position: 'absolute',
                        top: '-5px',
                        right: '-5px',
                        background: '#ff5252',
                        color: 'white',
                        fontSize: '10px',
                        width: '18px',
                        height: '18px',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 'bold'
                    }}>
                        {unreadCount}
                    </span>
                )}
            </div>

            {isOpen && (
                <div style={{
                    position: 'absolute',
                    top: '40px',
                    right: '0',
                    width: '300px',
                    background: 'white',
                    borderRadius: '10px',
                    boxShadow: '0 5px 20px rgba(0,0,0,0.1)',
                    padding: '10px',
                    zIndex: 1000,
                    border: '1px solid #eee'
                }}>
                    <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#333' }}>Notifications</h4>
                    {notifications.length === 0 ? (
                        <p style={{ fontSize: '12px', color: '#999', textAlign: 'center' }}>No new notifications</p>
                    ) : (
                        <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                            {notifications.map((n, i) => (
                                <div key={i} style={{
                                    padding: '8px',
                                    borderBottom: '1px solid #f5f5f5',
                                    fontSize: '12px',
                                    color: '#555'
                                }}>
                                    {n.message}
                                </div>
                            ))}
                        </div>
                    )}
                    <div
                        style={{ textAlign: 'center', marginTop: '10px', fontSize: '12px', color: '#009688', cursor: 'pointer' }}
                        onClick={clearNotifications}
                    >
                        Clear All
                    </div>
                </div>
            )}
        </div>
    );
}

export default NotificationBell;
