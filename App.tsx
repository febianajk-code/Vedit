
import React, { useState } from "react";
import {
  View,
  Text,
  ScrollView,
  Pressable,
  StyleSheet,
  SafeAreaView,
  StatusBar,
  Alert,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import { VideoView, useVideoPlayer } from "expo-video";

export default function App() {
  const [dark, setDark] = useState(true);
  const [video, setVideo] = useState<any>(null);
  const [playing, setPlaying] = useState(false);

  const bg = dark ? "#111316" : "#F4F5F7";
  const surface = dark ? "#1D2025" : "#FFFFFF";
  const text = dark ? "#F5F6F8" : "#17191D";
  const muted = dark ? "#9299A4" : "#777F8B";
  const border = dark ? "#30343B" : "#E5E7EB";
  const accent = dark ? "#DCE2EA" : "#252A32";

  // Player dibuat tanpa sumber awal.
  // Sumber video diatur saat pengguna memilih video.
  const player = useVideoPlayer(null, (p) => {
    p.loop = false;
  });

  // Import atau ganti video.
  const pickVideo = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ["videos"],
        allowsEditing: false,
        quality: 1,
      });

      if (!result.canceled && result.assets?.length) {
        const selectedVideo = result.assets[0];

        player.pause();
        await player.replaceAsync(selectedVideo.uri);

        setVideo(selectedVideo);
        setPlaying(false);
      }
    } catch (error) {
      Alert.alert(
        "Gagal memuat video",
        "Video tidak bisa dibuka. Coba pilih video lain."
      );
    }
  };

  // Putar atau jeda video.
  const togglePlayback = () => {
    if (!video) return;

    if (playing) {
      player.pause();
      setPlaying(false);
    } else {
      player.play();
      setPlaying(true);
    }
  };

  // Kembali ke halaman utama dan kosongkan player.
  const goHome = async () => {
    try {
      player.pause();
      await player.replaceAsync(null);
      setPlaying(false);
      setVideo(null);
    } catch (error) {
      Alert.alert("Error", "Gagal menutup video.");
    }
  };

  const styles = StyleSheet.create({
    screen: { flex: 1, backgroundColor: bg },
    content: {
      padding: 20,
      paddingBottom: 45,
      width: "100%",
      maxWidth: 700,
      alignSelf: "center",
    },
    header: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      marginBottom: 30,
    },
    brand: { color: text, fontSize: 25, fontWeight: "800" },
    subtitle: { color: muted, fontSize: 12, marginTop: 3 },
    button: {
      paddingHorizontal: 15,
      paddingVertical: 11,
      borderRadius: 15,
      backgroundColor: surface,
      borderWidth: 1,
      borderColor: border,
    },
    buttonText: { color: text, fontWeight: "700", fontSize: 13 },
    heading: { color: text, fontSize: 27, fontWeight: "800" },
    description: {
      color: muted,
      fontSize: 13,
      marginTop: 7,
      marginBottom: 23,
      lineHeight: 20,
    },
    card: {
      backgroundColor: surface,
      borderRadius: 22,
      padding: 17,
      borderWidth: 1,
      borderColor: border,
      marginBottom: 20,
    },
    preview: {
      height: 220,
      backgroundColor: "#08090B",
      borderRadius: 16,
      overflow: "hidden",
      justifyContent: "center",
      alignItems: "center",
      marginBottom: 15,
    },
    video: { width: "100%", height: "100%" },
    empty: { color: "#FFFFFF", fontSize: 13 },
    title: { color: text, fontSize: 17, fontWeight: "800" },
    muted: { color: muted, fontSize: 12, marginTop: 5 },
    primary: {
      backgroundColor: accent,
      borderRadius: 14,
      padding: 15,
      alignItems: "center",
      marginTop: 15,
    },
    primaryText: {
      color: dark ? "#15181D" : "#FFFFFF",
      fontSize: 14,
      fontWeight: "800",
    },
    section: {
      color: text,
      fontSize: 17,
      fontWeight: "800",
      marginBottom: 13,
    },
    timeline: {
      height: 75,
      borderRadius: 14,
      backgroundColor: dark ? "#292E35" : "#E9ECF1",
      justifyContent: "center",
      alignItems: "center",
      marginTop: 13,
    },
    timelineText: { color: muted, fontSize: 12 },
  });

  return (
    <SafeAreaView style={styles.screen}>
      <StatusBar
        barStyle={dark ? "light-content" : "dark-content"}
        backgroundColor={bg}
      />

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <View>
            <Text style={styles.brand}>Vedit</Text>
            <Text style={styles.subtitle}>A video editor by F13</Text>
          </View>

          <Pressable
            style={styles.button}
            onPress={() => setDark(!dark)}
          >
            <Text style={styles.buttonText}>
              {dark ? "☀ Light" : "☾ Dark"}
            </Text>
          </Pressable>
        </View>

        {!video ? (
          <>
            <Text style={styles.heading}>Create something.</Text>
            <Text style={styles.description}>
              Your creative space starts with a video.
            </Text>

            <View style={styles.card}>
              <Text style={styles.title}>Start a new project</Text>
              <Text style={styles.muted}>
                Import a video from your gallery.
              </Text>

              <Pressable style={styles.primary} onPress={pickVideo}>
                <Text style={styles.primaryText}>＋ Import video</Text>
              </Pressable>
            </View>
          </>
        ) : (
          <>
            <View style={styles.header}>
              <Pressable
                style={styles.button}
                onPress={goHome}
              >
                <Text style={styles.buttonText}>← Home</Text>
              </Pressable>

              <Text style={styles.title}>Editor</Text>
            </View>

            <View style={styles.preview}>
              <VideoView
                player={player}
                style={styles.video}
                contentFit="contain"
                nativeControls={false}
              />
            </View>

            <View style={styles.card}>
              <Text style={styles.title}>
                {video.fileName || "My video"}
              </Text>

              <Text style={styles.muted}>
                {video.duration
                  ? `${(video.duration / 1000).toFixed(1)} seconds`
                  : "Video imported"}
              </Text>

              <Pressable
                style={styles.primary}
                onPress={togglePlayback}
              >
                <Text style={styles.primaryText}>
                  {playing ? "Ⅱ  Pause" : "▶  Play"}
                </Text>
              </Pressable>
            </View>

            <Text style={styles.section}>Timeline</Text>

            <View style={styles.timeline}>
              <Text style={styles.timelineText}>
                Video clip · Timeline editing coming next
              </Text>
            </View>

            <Pressable
              style={[styles.button, { marginTop: 18 }]}
              onPress={pickVideo}
            >
              <Text style={styles.buttonText}>＋ Replace video</Text>
            </Pressable>
          </>
        )}

        <Text
          style={{
            color: muted,
            fontSize: 11,
            textAlign: "center",
            marginTop: 35,
          }}
        >
          Vedit 1.0 · Create without limits.
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}
