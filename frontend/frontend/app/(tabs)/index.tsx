import { StyleSheet, TextInput, ScrollView, Alert, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Text, View } from '@/components/Themed';
import axios from 'axios';
import * as DocumentPicker from 'expo-document-picker';
import { useRouter } from 'expo-router';
import { useState, useEffect } from 'react';

// Use correct IP (172.20.10.4)
const BACKEND_URL = "http://192.168.27.175:8000/api";

import AsyncStorage from '@react-native-async-storage/async-storage';

export default function RequestPassScreen() {
  const router = useRouter();

  // Pre-fill fields
  const [name, setName] = useState('');
  const [roll, setRoll] = useState('');
  const [department, setDepartment] = useState('');
  const [className, setClassName] = useState('');

  const [purpose, setPurpose] = useState('');
  const [leaveTime, setLeaveTime] = useState('');
  const [returnTime, setReturnTime] = useState('');
  const [proof, setProof] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // Load user data from AsyncStorage on mount
  useEffect(() => {
    const loadUser = async () => {
      try {
        const jsonValue = await AsyncStorage.getItem('user_session');
        if (jsonValue != null) {
          const userData = JSON.parse(jsonValue);
          setName(userData.name || userData.email || '');
          setRoll(userData.reg_no || '');
          setDepartment(userData.department || '');
          setClassName(userData.class || '');
        }
      } catch (e) {
        console.error("Failed to load user", e);
      }
    }
    loadUser();
  }, []);

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: '*/*',
        copyToCacheDirectory: true,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        setProof(result.assets[0]);
      }
    } catch (err) {
      console.log('Document picking failed', err);
    }
  };

  const handleRequest = async () => {
    if (!purpose || !leaveTime || !returnTime) {
      Alert.alert("Error", "Please fill in all required fields (Purpose, Leave Time, Return Time).");
      return;
    }
    if (!proof) {
      Alert.alert("Error", "Please upload a proof document.");
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('reg_no', roll);
      formData.append('purpose', purpose);
      formData.append('leave_time', leaveTime);
      formData.append('return_time', returnTime);

      formData.append('proof', {
        uri: proof.uri,
        name: proof.name,
        type: proof.mimeType || 'application/octet-stream',
      } as any);

      console.log("Sending Gate Pass Request...");

      const response = await axios.post(`${BACKEND_URL}/gate-pass/request`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.status === 'success') {
        Alert.alert("Success", "Gate Pass Approved!");
        // Clear fields
        setPurpose('');
        setLeaveTime('');
        setReturnTime('');
        setProof(null);

        // Navigate to My Pass tab
        router.push('/(tabs)/two');
      }
    } catch (error: any) {
      console.error(error);
      const msg = error.response?.data?.detail || "Failed to generate gate pass.";
      Alert.alert("Error", msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Request Gate Pass</Text>
      <Text style={styles.subtitle}>Verify details and submit leave application.</Text>

      <View style={styles.form}>
        {/* Read-Only User Details */}
        <Text style={styles.sectionHeader}>Student Details</Text>

        <View style={styles.row}>
          <View style={{ flex: 1, marginRight: 5 }}>
            <Text style={styles.label}>Full Name</Text>
            <TextInput style={[styles.input, styles.readOnly]} value={name} editable={false} />
          </View>
          <View style={{ flex: 1, marginLeft: 5 }}>
            <Text style={styles.label}>Roll No</Text>
            <TextInput style={[styles.input, styles.readOnly]} value={roll} editable={false} />
          </View>
        </View>

        <View style={styles.row}>
          <View style={{ flex: 1, marginRight: 5 }}>
            <Text style={styles.label}>Department</Text>
            <TextInput style={[styles.input, styles.readOnly]} value={department} editable={false} />
          </View>
          <View style={{ flex: 1, marginLeft: 5 }}>
            <Text style={styles.label}>Class</Text>
            <TextInput style={[styles.input, styles.readOnly]} value={className} editable={false} />
          </View>
        </View>

        {/* Input Fields */}
        <Text style={styles.sectionHeader}>Leave Details</Text>

        <Text style={styles.label}>Purpose of Leave</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g. Family Function, Medical"
          value={purpose}
          onChangeText={setPurpose}
        />

        <View style={styles.row}>
          <View style={{ flex: 1, marginRight: 5 }}>
            <Text style={styles.label}>Leave Time</Text>
            <TextInput
              style={styles.input}
              placeholder="10:00 AM"
              value={leaveTime}
              onChangeText={setLeaveTime}
            />
          </View>
          <View style={{ flex: 1, marginLeft: 5 }}>
            <Text style={styles.label}>Return Time</Text>
            <TextInput
              style={styles.input}
              placeholder="05:00 PM"
              value={returnTime}
              onChangeText={setReturnTime}
            />
          </View>
        </View>

        <Text style={styles.label}>Proof Document</Text>
        <TouchableOpacity style={styles.uploadButton} onPress={pickDocument}>
          <Text style={styles.uploadText}>
            {proof ? `✅ ${proof.name}` : "📄 Upload Proof (PDF/Image)"}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, loading && styles.disabledButton]}
          onPress={handleRequest}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.buttonText}>Submit Request</Text>
          )}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: '#f5f5f5',
    flexGrow: 1,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 20,
  },
  form: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionHeader: {
    fontSize: 16,
    fontWeight: '600',
    color: '#444',
    marginTop: 10,
    marginBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    paddingBottom: 5
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between'
  },
  label: {
    fontSize: 14,
    marginBottom: 5,
    color: '#444',
    fontWeight: '500',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginBottom: 15,
    backgroundColor: '#fff',
  },
  readOnly: {
    backgroundColor: '#f9f9f9',
    color: '#777'
  },
  uploadButton: {
    borderWidth: 1,
    borderColor: '#007AFF',
    borderStyle: 'dashed',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginBottom: 20,
    backgroundColor: '#f0f8ff'
  },
  uploadText: {
    color: '#007AFF',
    fontWeight: '600'
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  disabledButton: {
    opacity: 0.7,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
