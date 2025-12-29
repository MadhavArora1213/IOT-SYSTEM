import React, { useState, useEffect } from 'react';
import { StyleSheet, ActivityIndicator, Image } from 'react-native';
import QRCode from 'react-native-qrcode-svg';
import { Text, View } from '@/components/Themed';
import axios from 'axios';

const BACKEND_URL = "http://localhost:8000/api";

export default function MyPassScreen() {
  const [passData, setPassData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // In a real app, this would fetch the latest active pass for the logged-in user
  // For this demo, we can provide a "Generate Test Pass" button or just show placeholder
  const qrContent = passData ? `GATEPASS|${passData.qr_id}|${passData.roll}|${passData.name}` : "";

  return (
    <View style={styles.container}>
      <Text style={styles.title}>My active Pass</Text>
      <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" />

      {passData ? (
        <View style={styles.qrContainer}>
          <QRCode
            value={qrContent}
            size={250}
            color="black"
            backgroundColor="white"
          />
          <View style={styles.infoContainer}>
            <Text style={styles.infoLabel}>Name: <Text style={styles.infoValue}>{passData.name}</Text></Text>
            <Text style={styles.infoLabel}>Roll No: <Text style={styles.infoValue}>{passData.roll}</Text></Text>
            <Text style={styles.infoLabel}>Valid Till: <Text style={styles.infoValue}>{new Date(passData.valid_till).toLocaleTimeString()}</Text></Text>
          </View>
        </View>
      ) : (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>No active gate pass found.</Text>
          <Text style={styles.subText}>Please request a new pass from the home screen.</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 20,
  },
  separator: {
    marginVertical: 20,
    height: 1,
    width: '100%',
  },
  qrContainer: {
    alignItems: 'center',
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 20,
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  infoContainer: {
    marginTop: 20,
    width: '100%',
    backgroundColor: 'transparent',
  },
  infoLabel: {
    fontSize: 16,
    color: '#666',
    marginBottom: 5,
  },
  infoValue: {
    fontSize: 18,
    color: '#000',
    fontWeight: '600',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'transparent',
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#999',
  },
  subText: {
    fontSize: 14,
    color: '#bbb',
    marginTop: 10,
  },
});
