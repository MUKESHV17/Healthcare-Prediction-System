import { useState, useEffect, useRef } from 'react';
import { X, Send, Trash2 } from 'lucide-react';
import io from 'socket.io-client';

const socket = io('http://127.0.0.1:5001');

function ChatWindow({ isOpen, onClose, roomId, currentUserId, receiverId, contactName }) {
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState("");
    const messagesEndRef = useRef(null);

    useEffect(() => {
        if (isOpen && roomId) {
            socket.emit('join', { room: roomId });
            fetchHistory();
        }

        socket.on('receive_message', (msg) => {
            setMessages((prev) => [...prev, msg]);
            scrollToBottom();
        });

        socket.on('message_deleted', (data) => {
            setMessages(prev => prev.filter(m => m.id !== data.id));
        });

        return () => {
            socket.off('receive_message');
            socket.off('message_deleted');
            // socket.emit('leave', { room: roomId });
        };
    }, [isOpen, roomId]);

    const fetchHistory = async () => {
        try {
            const res = await fetch(`http://127.0.0.1:5001/chat/history/${roomId}`);
            const data = await res.json();
            setMessages(data);
            scrollToBottom();
        } catch (err) {
            console.error("Failed to fetch history", err);
        }
    };

    const sendMessage = () => {
        if (!newMessage.trim()) return;

        const msgData = {
            room: roomId,
            senderId: currentUserId,
            receiverId: receiverId,
            content: newMessage
        };

        socket.emit('send_message', msgData);
        setNewMessage("");
    };

    const deleteMessage = (msgId) => {
        if (window.confirm("Delete this message for everyone?")) {
            socket.emit('delete_message', { id: msgId, room: roomId });
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    if (!isOpen) return null;

    return (
        <div style={{
            position: 'fixed',
            bottom: '80px',
            right: '20px',
            width: '350px',
            height: '500px',
            background: 'white',
            borderRadius: '15px',
            boxShadow: '0 5px 25px rgba(0,0,0,0.2)',
            display: 'flex',
            flexDirection: 'column',
            zIndex: 1000,
            overflow: 'hidden',
            border: '1px solid #eee'
        }}>
            {/* Header */}
            <div style={{
                padding: '15px',
                background: '#009688',
                color: 'white',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderTopLeftRadius: '15px',
                borderTopRightRadius: '15px'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{ width: '10px', height: '10px', background: '#00e676', borderRadius: '50%' }}></div>
                    <span style={{ fontWeight: 'bold' }}>{contactName}</span>
                </div>
                <X size={20} style={{ cursor: 'pointer' }} onClick={onClose} />
            </div>

            {/* Messages Area */}
            <div style={{
                flex: 1,
                padding: '15px',
                overflowY: 'auto',
                background: '#f5f7fa',
                display: 'flex',
                flexDirection: 'column',
                gap: '10px'
            }}>
                {messages.map((msg, index) => {
                    const isMe = msg.senderId === currentUserId;
                    return (
                        <div key={index} style={{
                            alignSelf: isMe ? 'flex-end' : 'flex-start',
                            maxWidth: '75%',
                            display: 'flex',
                            flexDirection: 'column'
                        }}>
                            <div style={{
                                background: isMe ? '#009688' : 'white',
                                color: isMe ? 'white' : '#333',
                                padding: '10px 14px',
                                borderRadius: isMe ? '15px 15px 0 15px' : '15px 15px 15px 0',
                                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                                position: 'relative',
                                wordBreak: 'break-word'
                            }}>
                                {msg.content}
                                {isMe && (
                                    <Trash2
                                        size={12}
                                        style={{
                                            position: 'absolute',
                                            top: '-15px',
                                            right: '0',
                                            cursor: 'pointer',
                                            color: '#ff5252',
                                            display: 'none' // Hover logic hard in inline styles, maybe add separate button
                                        }}
                                        onClick={() => deleteMessage(msg.id)}
                                    />
                                )}
                            </div>
                            <div style={{
                                display: 'flex',
                                justifyContent: isMe ? 'flex-end' : 'flex-start',
                                gap: '5px',
                                marginTop: '2px'
                            }}>
                                <span style={{ fontSize: '10px', color: '#999' }}>{msg.timestamp}</span>
                                {isMe && <span style={{ fontSize: '10px', color: '#ff5252', cursor: 'pointer' }} onClick={() => deleteMessage(msg.id)}>Delete</span>}
                            </div>
                        </div>
                    );
                })}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div style={{
                padding: '15px',
                background: 'white',
                borderTop: '1px solid #eee',
                display: 'flex',
                gap: '10px',
                alignItems: 'center'
            }}>
                <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Type a message..."
                    style={{
                        flex: 1,
                        padding: '10px',
                        borderRadius: '20px',
                        border: '1px solid #ddd',
                        outline: 'none'
                    }}
                />
                <button
                    onClick={sendMessage}
                    style={{
                        background: '#009688',
                        color: 'white',
                        border: 'none',
                        width: '40px',
                        height: '40px',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: 'pointer'
                    }}
                >
                    <Send size={18} />
                </button>
            </div>
        </div>
    );
}

export default ChatWindow;
