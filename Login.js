// ... (Previous imports)
export default function Login({ navigation }) {
  // ... (Previous states and functions)

  return (
    <View style={styles.container}>
      <Text style={styles.logo}>VIBE</Text>
      {/* ... (Previous Inputs and Login Button) */}
      
      <TouchableOpacity onPress={() => navigation.navigate("ForgotID")}>
        <Text style={{color:'#444', marginTop:20}}>Forgot UserID?</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={() => navigation.navigate("ResetPassword")}>
        <Text style={{color:'#444', marginTop:10}}>Forgot Password?</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={onSignup}>
        <Text style={{color:'#888', marginTop:30}}>Create New Identity</Text>
      </TouchableOpacity>
    </View>
  );
}