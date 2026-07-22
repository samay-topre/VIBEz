import React, { useState, useEffect, useRef } from 'react';
import { View, Text, TextInput, TouchableOpacity, FlatList, StyleSheet, ScrollView, Dimensions } from 'react-native';
import axios from 'axios';

const { width } = Dimensions.get('window');
const API = "http://YOUR_PC_IP:8000";

const CATEGORIES = ["Dating", "Relationship", "Marriage", "Toxic/Red Flags", "Exes", "Corporate", "Boss", "Coworkers", "Finance", "Freelancers", "College", "Professors", "Health", "Fitness", "Landlords", "Roommates", "Cafes", "Hotels", "Society", "Shopping", "Others"];

export default function Home({ route }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [stream, setStream] = useState([]);
  const [selectedCat, setSelectedCat] = useState("Dating");
  const [placeholder, setPlaceholder] = useState("Search...");
  
  const scrollRef = useRef();
  const offset = useRef(0);

  // 1. GHOST PLACEHOLDER LOGIC
  useEffect(() => {
    const ghosts = ["Dating Rakesh from Indore?", "Toxic boss at Accenture?", "Landlord of Flat 402?"];
    let i = 0;
    const interval = setInterval(() => { setPlaceholder(ghosts[i % 3]); i++; }, 3000);
    fetchStream();
    return () => clearInterval(interval);
  }, []);

  // 2. AUTO-SCROLLING "BIG BOX" LOGIC
  useEffect(() => {
    if (stream.length > 0) {
      const scrollInterval = setInterval(() => {
        offset.current += 1;
        if (offset.current > 2000) offset.current = 0; // Reset when end reached
        scrollRef.current?.scrollToOffset({ offset: offset.current, animated: false });
      }, 30); // Speed control
      return () => clearInterval(scrollInterval);
    }
  }, [stream]);

  const fetchStream = async () => {
    try {
        const res = await axios.get(`${API}/vibe-stream`);
        setStream([...res.data, ...res.data]); // Duplicate for infinite feel
    } catch (e) { console.log("Stream Error", e); }
  };

  const onSearch = async () => {
    const res = await axios.get(`${API}/search?query=${query}&category=${selectedCat}`);
    setResults(res.data);
  };

  return (
    <View style={styles.container}>
      {/* THE BIG BOX: VIBE SHOWCASE (Auto-Scrolling) */}
      <View style={styles.marqueeContainer}>
        <FlatList
          ref={scrollRef}
          data={stream}
          keyExtractor={(_, i) => i.toString()}
          showsVerticalScrollIndicator={false}
          renderItem={({ item }) => (
            <View style={styles.streamCard}>
              <Text style={styles.streamCat}>{item.category}</Text>
              <Text style={styles.streamText}>{item.content}</Text>
              <Text style={styles.streamUser}>by !@#*** • Just now</Text>
            </View>
          )}
        />
      </View>

      {/* CATEGORY SELECTOR (21 Items) */}
      <View style={{height: 50}}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {CATEGORIES.map(c => (
                <TouchableOpacity key={c} onPress={() => setSelectedCat(c)} 
                    style={[styles.catBtn, selectedCat === c && {backgroundColor: '#fff'}]}>
                    <Text style={{color: selectedCat === c ? '#000' : '#888'}}>{c}</Text>
                </TouchableOpacity>
            ))}
        </ScrollView>
      </View>

      {/* SEARCH BOX */}
      <View style={styles.searchBox}>
        <TextInput style={styles.input} placeholder={placeholder} placeholderTextColor="#444" onChangeText={setQuery} value={query} />
        <TouchableOpacity style={styles.refresh} onPress={() => setQuery('')}><Text style={{color:'#fff'}}>X</Text></TouchableOpacity>
        <TouchableOpacity style={styles.sbtn} onPress={onSearch}><Text style={{fontWeight:'bold'}}>CHECK</Text></TouchableOpacity>
      </View>

      {/* RESULTS (3 BELTS) */}
      {results && (
        <ScrollView style={{flex: 1, padding: 15}}>
          {['High', 'Mid', 'Low'].map(belt => (
            <View key={belt} style={{marginBottom: 20}}>
              <Text style={styles.beltLabel}>{belt.toUpperCase()} VIBE MATCH</Text>
              {results[belt].map(r => (
                <View key={r.id} style={styles.resultCard}>
                  <Text style={{color:'#fff', fontSize: 14}}>{r.text}</Text>
                  <Text style={{color:'#444', fontSize: 10, marginTop: 5}}>by {r.by} • {r.score}</Text>
                </View>
              ))}
            </View>
          ))}
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000', paddingTop: 40 },
  marqueeContainer: { height: 200, backgroundColor: '#080808', borderBottomWidth: 1, borderColor: '#1a1a1a' },
  streamCard: { padding: 15, borderBottomWidth: 1, borderColor: '#111' },
  streamCat: { color: '#ef4444', fontSize: 10, fontWeight: 'bold' },
  streamText: { color: '#888', fontSize: 12, marginVertical: 3 },
  streamUser: { color: '#333', fontSize: 9 },
  catBtn: { paddingHorizontal: 15, paddingVertical: 8, marginHorizontal: 5, borderRadius: 20, borderWidth: 1, borderColor: '#222', height: 35 },
  searchBox: { padding: 15, flexDirection: 'row', alignItems: 'center' },
  input: { flex: 1, height: 50, backgroundColor: '#111', color: '#fff', borderRadius: 10, paddingHorizontal: 15 },
  refresh: { marginHorizontal: 10 },
  sbtn: { backgroundColor: '#fff', padding: 15, borderRadius: 10 },
  beltLabel: { color: '#444', fontSize: 11, marginBottom: 10, letterSpacing: 1 },
  resultCard: { backgroundColor: '#111', padding: 15, borderRadius: 12, marginBottom: 10, borderLeftWidth: 3, borderLeftColor: '#ef4444' }
});