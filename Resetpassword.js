import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import axios from 'axios';

const API = "http://YOUR_PC_IP:8000";

export default function ResetPassword({ navigation }) {
  const [uid, setUid] = useState('');
  const [email, setEmail] = useState('');

  const handleReset = async () => {
    try {
      // Logic: Backend checks if UID + Email match a single record
      await axios.post(`${API}/forgot-password-request?user_id_alias=${uid}&email=${email}`);
      Alert.alert("Check Email", "A password reset link has been sent.");
      navigation.goBack();
    } catch (e) { Alert.alert("Failed", "ID and Email mismatch."); }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Reset Password</Text>
      <Text style={styles.sub}>Enter your Symbol-ID and Registered Email.</Text>
      <TextInput placeholder="!@#123 (Your ID)" placeholderTextColor="#444" style={styles.input} onChangeText={setUid} />
      <TextInput placeholder="Registered Email" placeholderTextColor="#444" style={styles.input} onChangeText={setEmail} />
      <TouchableOpacity style={styles.btn} onPress={handleReset}><Text style={styles.btnTxt}>REQUEST RESET</Text></TouchableOpacity>
      <TouchableOpacity onPress={() => navigation.goBack()}><Text style={{color: '#888', marginTop: 20}}>Back to Login</Text></TouchableOpacity>
    </View>
  );
}
// (Uses same styles as ForgotID)
const styles = StyleSheet.create({ /* Paste styles from ForgotID here */ });