import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import axios from 'axios';

const API = "http://YOUR_PC_IP:8000"; 

export default function ForgotID({ navigation }) {
  const [email, setEmail] = useState('');

  const handleRecover = async () => {
    try {
      await axios.post(`${API}/recover-id?email=${email}`);
      Alert.alert("Sent", "If this email is registered, your IDs have been sent.");
      navigation.goBack();
    } catch (e) { Alert.alert("Error", "Could not connect to server."); }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Recover UserID</Text>
      <Text style={styles.sub}>Enter your email to receive all linked symbol-IDs.</Text>
      <TextInput placeholder="Registered Email" placeholderTextColor="#444" style={styles.input} onChangeText={setEmail} />
      <TouchableOpacity style={styles.btn} onPress={handleRecover}><Text style={styles.btnTxt}>SEND EMAIL</Text></TouchableOpacity>
      <TouchableOpacity onPress={() => navigation.goBack()}><Text style={{color: '#888', marginTop: 20}}>Back to Login</Text></TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#050505', alignItems: 'center', justifyContent: 'center' },
  title: { color: '#fff', fontSize: 24, fontWeight: 'bold', marginBottom: 10 },
  sub: { color: '#555', textAlign: 'center', width: '80%', marginBottom: 30 },
  input: { width: '85%', height: 55, backgroundColor: '#111', borderRadius: 12, color: '#fff', paddingHorizontal: 15, marginBottom: 15, borderWidth: 1, borderColor: '#222' },
  btn: { width: '85%', height: 55, backgroundColor: '#fff', borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
  btnTxt: { fontWeight: 'bold' }
});