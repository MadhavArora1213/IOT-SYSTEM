import { StyleSheet, Image, ActivityIndicator, ScrollView, RefreshControl } from 'react-native';
import { Text, View } from '@/components/Themed';
import axios from 'axios';
import { useLocalSearchParams, useFocusEffect } from 'expo-router';
import { useState, useCallback } from 'react';

const BACKEND_URL = "http://192.168.27.175:8000"; // Base URL without /api, to access /images

import AsyncStorage from '@react-native-async-storage/async-storage';

export default function MyPassScreen() {
  const params = useLocalSearchParams();
  const [passData, setPassData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchPasses = async () => {
    try {
      // Get user from storage
      const jsonValue = await AsyncStorage.getItem('user_session');
      if (jsonValue == null) {
        setLoading(false);
        return;
      }
      const userData = JSON.parse(jsonValue);
      const regNo = userData.reg_no;

      if (!regNo) {
        setLoading(false);
        return;
      }

      const response = await axios.get(`${BACKEND_URL}/api/gate-pass/my-passes/${regNo}`);
      if (response.data.status === 'success' && response.data.data.length > 0) {
        setPassData(response.data.data[0]);
      }
    } catch (error) {
      console.error("Failed to fetch passes", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchPasses();
    }, [])
  );

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchPasses();
  }, []);

  if (loading) {
    return <View style={styles.center}><ActivityIndicator size="large" color="#007AFF" /></View>;
  }

  if (!passData) {
    return (
      <View style={styles.center}>
        <Text style={styles.noPassText}>No active gate pass found.</Text>
        <Text style={styles.subText}>Apply for a pass in the Home tab.</Text>
      </View>
    );
  }

  const profileImageUrl = passData.profile_image ? `${BACKEND_URL}/images/${passData.profile_image}` : null;
  const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${passData.pass_id}`;

  return (
    <ScrollView
      contentContainerStyle={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={styles.card}>
        <View style={styles.header}>
          <Text style={styles.collegeName}>UNIVERSITY GATE PASS</Text>
          <View style={[styles.statusBadge, { backgroundColor: passData.status === 'APPROVED' ? '#e6fffa' : '#fff5f5' }]}>
            <Text style={[styles.statusText, { color: passData.status === 'APPROVED' ? '#047857' : '#c53030' }]}>
              {passData.status}
            </Text>
          </View>
        </View>

        <View style={styles.profileSection}>
          {profileImageUrl ? (
            <Image source={{ uri: profileImageUrl }} style={styles.profileImage} />
          ) : (
            <View style={[styles.profileImage, { backgroundColor: '#ccc' }]} />
          )}
          <Text style={styles.studentName}>{passData.name}</Text>
          <Text style={styles.regNo}>{passData.reg_no}</Text>
        </View>

        <View style={styles.detailsGrid}>
          <DetailItem label="Department" value={passData.department} />
          <DetailItem label="Class" value={passData.class} />
          <DetailItem label="Date" value={new Date(passData.created_at).toLocaleDateString()} />
          <DetailItem label="Purpose" value={passData.purpose} />
          <DetailItem label="Leave Time" value={passData.leave_time} />
          <DetailItem label="Return Time" value={passData.return_time} />
        </View>

        <View style={styles.qrSection}>
          <Image source={{ uri: qrUrl }} style={styles.qrCode} />
          <Text style={styles.scanText}>Scan at Gate</Text>
        </View>
      </View>
    </ScrollView>
  );
}

const DetailItem = ({ label, value }: { label: string, value: string }) => (
  <View style={styles.detailItem}>
    <Text style={styles.label}>{label}</Text>
    <Text style={styles.value} numberOfLines={1}>{value}</Text>
  </View>
);

const styles = StyleSheet.create({
  container: {
    padding: 15,
    backgroundColor: '#f3f4f6',
    flexGrow: 1,
    alignItems: 'center',
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  card: {
    width: '100%',
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
    paddingBottom: 15
  },
  collegeName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
    textTransform: 'uppercase'
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: 'bold',
    textTransform: 'uppercase'
  },
  profileSection: {
    alignItems: 'center',
    marginBottom: 25
  },
  profileImage: {
    width: 100,
    height: 100,
    borderRadius: 50,
    marginBottom: 10,
    borderWidth: 3,
    borderColor: '#f0f9ff'
  },
  studentName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827'
  },
  regNo: {
    fontSize: 14,
    color: '#6b7280'
  },
  detailsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 20
  },
  detailItem: {
    width: '48%',
    marginBottom: 15,
    backgroundColor: '#f9fafb',
    padding: 10,
    borderRadius: 8
  },
  label: {
    fontSize: 12,
    color: '#9ca3af',
    marginBottom: 2,
    textTransform: 'uppercase'
  },
  value: {
    fontSize: 14,
    color: '#374151',
    fontWeight: '600'
  },
  qrSection: {
    alignItems: 'center',
    marginTop: 10,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    paddingTop: 20
  },
  qrCode: {
    width: 180,
    height: 180,
  },
  scanText: {
    marginTop: 10,
    color: '#9ca3af',
    fontSize: 12
  },
  noPassText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#4b5563'
  },
  subText: {
    marginTop: 8,
    color: '#9ca3af'
  }
});
