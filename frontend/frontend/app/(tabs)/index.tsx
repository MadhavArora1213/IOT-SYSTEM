import React, { useState, useRef } from 'react';
import { StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator, Image } from 'react-native';
import { Text, View } from '@/components/Themed';
import axios from 'axios';
import { CameraView, useCameraPermissions } from 'expo-camera';

const BACKEND_URL = "http://localhost:8000/api";

export default function RequestPassScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const [name, setName] = useState('');
  const [roll, setRoll] = useState('');
  const [reason, setReason] = useState('');
  const [destination, setDestination] = useState('');
  const [loading, setLoading] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const cameraRef = useRef<any>(null);

  const handleRequest = async () => {
    if (!name || !roll) {
      Alert.alert("Error", "Name and Roll Number are required.");
      return;
    }
    if (!capturedImage) {
      Alert.alert("Error", "Please capture your photo for identity verification.");
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('name', name);
      formData.append('roll', roll);

      // Append image
      const filename = capturedImage.split('/').pop() || 'photo.jpg';
      const match = /\.(\w+)$/.exec(filename);
      const type = match ? `image/${match[1]}` : `image`;

      formData.append('registration_image', {
        uri: capturedImage,
        name: filename,
        type: type,
      } as any);

      const response = await axios.post(`${BACKEND_URL}/register-qr`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data) {
        Alert.alert("Success", "Gate Pass generated with Face Identity!");
        setCapturedImage(null);
        setName('');
        setRoll('');
      }
    } catch (error: any) {
      console.error(error);
      Alert.alert("Error", "Failed to generate gate pass. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const takePicture = async () => {
    if (cameraRef.current) {
      const photo = await cameraRef.current.takePictureAsync();
      setCapturedImage(photo.uri);
      setShowCamera(false);
    }
  };

  if (showCamera) {
    if (!permission) return <View />;
    if (!permission.granted) {
      return (
        <View style={styles.container}>
          <Text style={{ textAlign: 'center' }}>We need your permission to show the camera</Text>
          <TouchableOpacity onPress={requestPermission} style={styles.button}>
            <Text style={styles.buttonText}>Grant Permission</Text>
          </TouchableOpacity>
        </View>
      );
    }
    return (
      <View style={styles.cameraContainer}>
        <CameraView style={styles.camera} facing="front" ref={cameraRef}>
          <View style={styles.cameraOverlay}>
            <TouchableOpacity style={styles.captureButton} onPress={takePicture}>
              <View style={styles.captureInner} />
            </TouchableOpacity>
            <TouchableOpacity style={styles.cancelButton} onPress={() => setShowCamera(false)}>
              <Text style={{ color: 'white' }}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </CameraView>
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Request Gate Pass</Text>
      <Text style={styles.subtitle}>Fill in details and capture your photo for verification.</Text>

      <View style={styles.form}>
        <Text style={styles.label}>Full Name</Text>
        <TextInput
          style={styles.input}
          placeholder="Enter your name"
          value={name}
          onChangeText={setName}
        />

        <Text style={styles.label}>Roll Number / ID</Text>
        <TextInput
          style={styles.input}
          placeholder="Enter roll number"
          value={roll}
          onChangeText={setRoll}
        />

        <Text style={styles.label}>Photo Identity</Text>
        {capturedImage ? (
          <View style={styles.previewContainer}>
            <Image source={{ uri: capturedImage }} style={styles.preview} />
            <TouchableOpacity onPress={() => setShowCamera(true)} style={styles.reTakeButton}>
              <Text style={styles.reTakeText}>Retake Photo</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <TouchableOpacity style={styles.cameraTrigger} onPress={() => setShowCamera(true)}>
            <Text style={styles.cameraTriggerText}>📸 Capture Live Photo</Text>
          </TouchableOpacity>
        )}

        <TouchableOpacity
          style={[styles.button, (!capturedImage || loading) && styles.disabledButton]}
          onPress={handleRequest}
          disabled={loading || !capturedImage}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.buttonText}>Generate Pass</Text>
          )}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 20,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 10,
    marginBottom: 30,
  },
  form: {
    backgroundColor: 'transparent',
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#555',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginBottom: 20,
    backgroundColor: '#f9f9f9',
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 18,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20,
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  cameraTrigger: {
    height: 120,
    borderWidth: 2,
    borderColor: '#007AFF',
    borderStyle: 'dashed',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    backgroundColor: '#f0f7ff',
  },
  cameraTriggerText: {
    color: '#007AFF',
    fontWeight: '600',
  },
  previewContainer: {
    alignItems: 'center',
    marginBottom: 20,
    backgroundColor: 'transparent',
  },
  preview: {
    width: '100%',
    height: 250,
    borderRadius: 12,
  },
  reTakeButton: {
    marginTop: 10,
    padding: 8,
  },
  reTakeText: {
    color: '#FF3B30',
    fontWeight: '600',
  },
  cameraContainer: {
    flex: 1,
    backgroundColor: 'black',
  },
  camera: {
    flex: 1,
  },
  cameraOverlay: {
    flex: 1,
    backgroundColor: 'transparent',
    justifyContent: 'flex-end',
    alignItems: 'center',
    paddingBottom: 50,
  },
  captureButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'white',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureInner: {
    width: 70,
    height: 70,
    borderRadius: 35,
    borderWidth: 2,
    borderColor: 'black',
  },
  cancelButton: {
    position: 'absolute',
    top: 50,
    left: 20,
    padding: 10,
  }
});
