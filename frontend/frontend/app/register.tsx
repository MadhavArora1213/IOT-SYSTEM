import React, { useState, useRef } from 'react';
import { StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator, Image, Modal } from 'react-native';
import { Text, View } from '@/components/Themed';
import { CameraView, useCameraPermissions } from 'expo-camera';
import axios from 'axios';
import { router } from 'expo-router';

const BACKEND_URL = "http://192.168.27.175:8000/api";

export default function RegisterScreen() {
    const [permission, requestPermission] = useCameraPermissions();
    const [showCamera, setShowCamera] = useState(false);
    const cameraRef = useRef<any>(null);

    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        reg_no: '',
        password: '',
        email: '',
        phone: '',
        class: '',
        department: '',
        hod_name: '',
        incharge_name: '',
        valid_until: '',
    });
    const [capturedImage, setCapturedImage] = useState<string | null>(null);

    const handleChange = (name: string, value: string) => {
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const takePicture = async () => {
        if (cameraRef.current) {
            const photo = await cameraRef.current.takePictureAsync();
            setCapturedImage(photo.uri);
            setShowCamera(false);
        }
    };

    const handleRegister = async () => {
        // Basic validation
        if (!formData.reg_no || !formData.password || !formData.email) {
            Alert.alert("Error", "Please fill in all required fields.");
            return;
        }
        if (!capturedImage) {
            Alert.alert("Error", "Please capture a profile image.");
            return;
        }

        setLoading(true);
        try {
            const data = new FormData();
            Object.keys(formData).forEach(key => {
                data.append(key === 'class' ? 'class_name' : key, (formData as any)[key]);
            });

            // Append image
            const filename = capturedImage.split('/').pop() || 'photo.jpg';
            const match = /\.(\w+)$/.exec(filename);
            const type = match ? `image/${match[1]}` : `image/jpeg`;

            data.append('image', {
                uri: capturedImage,
                name: filename,
                type: type,
            } as any);

            const response = await axios.post(`${BACKEND_URL}/users/register`, data, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            if (response.data.status === 'success') {
                Alert.alert("Success", "Registration Successful! Please Login.");
                router.back(); // Go back to Login
            }
        } catch (error: any) {
            console.error(error);
            const msg = error.response?.data?.detail || "Registration failed.";
            Alert.alert("Error", msg);
        } finally {
            setLoading(false);
        }
    };

    if (showCamera) {
        if (!permission) return <View />;
        if (!permission.granted) {
            requestPermission();
            return <View />;
        }
        return (
            <View style={styles.cameraContainer}>
                <CameraView style={styles.camera} facing="front" ref={cameraRef} />
                <View style={styles.cameraOverlay}>
                    <TouchableOpacity style={styles.captureButton} onPress={takePicture}>
                        <View style={styles.captureInner} />
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.cancelButton} onPress={() => setShowCamera(false)}>
                        <Text style={{ color: 'white' }}>Cancel</Text>
                    </TouchableOpacity>
                </View>
            </View>
        );
    }

    return (
        <ScrollView contentContainerStyle={styles.container}>
            <Text style={styles.title}>Register</Text>

            <View style={styles.form}>
                <TextInput style={styles.input} placeholder="Registration Number *" value={formData.reg_no} onChangeText={t => handleChange('reg_no', t)} />
                <TextInput style={styles.input} placeholder="Password *" value={formData.password} onChangeText={t => handleChange('password', t)} secureTextEntry />
                <TextInput style={styles.input} placeholder="Email *" value={formData.email} onChangeText={t => handleChange('email', t)} keyboardType="email-address" />
                <TextInput style={styles.input} placeholder="Phone Number" value={formData.phone} onChangeText={t => handleChange('phone', t)} keyboardType="phone-pad" />
                <TextInput style={styles.input} placeholder="Class" value={formData.class} onChangeText={t => handleChange('class', t)} />
                <TextInput style={styles.input} placeholder="Department" value={formData.department} onChangeText={t => handleChange('department', t)} />
                <TextInput style={styles.input} placeholder="HOD Name" value={formData.hod_name} onChangeText={t => handleChange('hod_name', t)} />
                <TextInput style={styles.input} placeholder="Incharge Name" value={formData.incharge_name} onChangeText={t => handleChange('incharge_name', t)} />
                <TextInput style={styles.input} placeholder="Valid Until (YYYY-MM-DD)" value={formData.valid_until} onChangeText={t => handleChange('valid_until', t)} />

                <Text style={styles.label}>Profile Image *</Text>
                {capturedImage ? (
                    <View style={styles.previewContainer}>
                        <Image source={{ uri: capturedImage }} style={styles.preview} />
                        <TouchableOpacity onPress={() => setShowCamera(true)} style={styles.reTakeButton}>
                            <Text style={styles.reTakeText}>Retake Photo</Text>
                        </TouchableOpacity>
                    </View>
                ) : (
                    <TouchableOpacity style={styles.cameraTrigger} onPress={() => setShowCamera(true)}>
                        <Text style={styles.cameraTriggerText}>📸 Capture Photo</Text>
                    </TouchableOpacity>
                )}

                <TouchableOpacity style={styles.button} onPress={handleRegister} disabled={loading}>
                    {loading ? <ActivityIndicator color="white" /> : <Text style={styles.buttonText}>Register</Text>}
                </TouchableOpacity>
            </View>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        padding: 20,
        paddingBottom: 50,
        backgroundColor: '#fff',
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        marginBottom: 20,
        textAlign: 'center',
        color: '#333',
    },
    form: {
        backgroundColor: 'transparent',
    },
    input: {
        borderWidth: 1,
        borderColor: '#ddd',
        borderRadius: 8,
        padding: 12,
        fontSize: 16,
        marginBottom: 15,
        backgroundColor: '#f9f9f9',
    },
    label: {
        marginBottom: 10,
        fontWeight: '600',
        color: '#555',
    },
    button: {
        backgroundColor: '#007AFF',
        padding: 15,
        borderRadius: 8,
        alignItems: 'center',
        marginTop: 20,
    },
    buttonText: {
        color: 'white',
        fontSize: 18,
        fontWeight: 'bold',
    },
    cameraContainer: {
        flex: 1,
        backgroundColor: 'black',
    },
    camera: {
        flex: 1,
    },
    cameraOverlay: {
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: 150,
        backgroundColor: 'transparent',
        justifyContent: 'center',
        alignItems: 'center',
        paddingBottom: 20,
    },
    captureButton: {
        width: 80,
        height: 80,
        borderRadius: 40,
        backgroundColor: 'white',
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
    },
    cameraTrigger: {
        height: 100,
        borderWidth: 1,
        borderColor: '#007AFF',
        borderStyle: 'dashed',
        borderRadius: 12,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#f0f7ff',
        marginBottom: 10,
    },
    cameraTriggerText: {
        color: '#007AFF',
        fontWeight: '600',
    },
    previewContainer: {
        alignItems: 'center',
        marginBottom: 10,
        backgroundColor: 'transparent',
    },
    preview: {
        width: 150,
        height: 150,
        borderRadius: 75,
    },
    reTakeButton: {
        marginTop: 10,
    },
    reTakeText: {
        color: '#FF3B30',
    },
});
