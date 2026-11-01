import React, { useEffect, useState } from "react";
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

type VideoAsset = ImagePicker.ImagePickerAsset;

const formatTime = (seconds: number) => {
  const safe = Math.max(0, seconds);
  const minutes = Math.floor(safe / 60);
  const remaining = Math.floor(safe % 60);
  const tenths = Math.floor((safe % 1) * 10);

  return `${minutes}:${String(remaining).padStart(2, "0")}.${tenths}`;
};

export default function App() {
  const [dark, setDark] = useState(true);
  const [video, setVideo] = useState<VideoAsset | null>(null);
  const [playing, setPlaying] = useState(false);
  const [loading, setLoading] = useState(false);

  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [trimIn, setTrimIn] = useState(0);
  const [trimOut, setTrimOut] = useState(0);
  const [previewingTrim, setPreviewingTrim] = useState(false);
  const [timelineWidth, setTimelineWidth] = useState(1);

  const bg = dark ? "#111316" : "#F4F5F7";
  const surface = dark ? "#1D2025" : "#FFFFFF";
  const text = dark ? "#F5F6F8" : "#17191D";
  const muted = dark ? "#9299A4" : "#777F8B";
  const border = dark ? "#30343B" : "#E5E7EB";
  const accent = dark ? "#DCE2EA" : "#252A32";

  const player = useVideoPlayer(null, (p) => {
    p.loop = false;
    p.timeUpdateEventInterval = 0.15;
  });

  useEffect(() => {
    const playingSubscription = player.addListener(
      "playingChange",
      ({ isPlaying }) => {
        setPlaying(isPlaying);
      }
    );

    return () => playingSubscription.remove();
  }, [player]);

  useEffect(() => {
    const timeSubscription = player.addListener(
      "timeUpdate",
      ({ currentTime: time }) => {
        setCurrentTime(time);

        if (previewingTrim && time >= trimOut) {
          player.pause();
          player.currentTime = trimIn;
          setCurrentTime(trimIn);
          setPreviewingTrim(false);
        }
      }
    );

    const sourceSubscription = player.addListener(
      "sourceLoad",
      ({ duration: loadedDuration }) => {
        if (loadedDuration > 0) {
          setDuration(loadedDuration);
          setTrimIn(0);
          setTrimOut(loadedDuration);
        }
      }
    );

    return () => {
      timeSubscription.remove();
      sourceSubscription.remove();
    };
  }, [player, previewingTrim, trimIn, trimOut]);

  const pickVideo = async () => {
    if (loading) return;

    try {
      setLoading(true);

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ["videos"],
        allowsEditing: false,
        quality: 1,
      });

      if (result.canceled || !result.assets?.length) return;

      const selectedVideo = result.assets[0];

      player.pause();
      setPreviewingTrim(false);

      await player.replaceAsync(selectedVideo.uri);

      const estimatedDuration = (selectedVideo.duration || 0) / 1000;

      setVideo(selectedVideo);
      setCurrentTime(0);
      setDuration(estimatedDuration);
      setTrimIn(0);
      setTrimOut(estimatedDuration);
    } catch {
      Alert.alert(
        "Gagal memuat video",
        "Video tidak bisa dibuka. Coba pilih video lain."
      );
    } finally {
      setLoading(false);
    }
  };

  const togglePlayback = () => {
    if (!video || loading) return;

    setPreviewingTrim(false);

    if (player.playing) {
      player.pause();
    } else {
      player.play();
    }
  };

  const seekTo = (time: number) => {
    if (!duration) return;

    const target = Math.max(0, Math.min(time, duration));
    player.currentTime = target;
    setCurrentTime(target);
  };

  const markStart = () => {
    if (!duration) return;

    if (currentTime >= trimOut) {
      Alert.alert(
        "Posisi tidak valid",
        "Titik awal harus berada sebelum titik akhir."
      );
      return;
    }

    setTrimIn(currentTime);
  };

  const markEnd = () => {
    if (!duration) return;

    if (currentTime <= trimIn) {
      Alert.alert(
        "Posisi tidak valid",
        "Titik akhir harus berada setelah titik awal."
      );
      return;
    }

    setTrimOut(currentTime);
  };

  const previewSelection = () => {
    if (!duration || trimOut <= trimIn) {
      Alert.alert("Rentang tidak valid", "Atur titik awal dan akhir dulu.");
      return;
    }

    player.pause();
    player.currentTime = trimIn;
    setCurrentTime(trimIn);
    setPreviewingTrim(true);
    player.play();
  };

  const goHome = () => {
    player.pause();
    setPreviewingTrim(false);
    setPlaying(false);
    setVideo(null);
    setCurrentTime(0);
    setDuration(0);
    setTrimIn(0);
    setTrimOut(0);
  };

  const styles = StyleSheet.create({
    screen: {
      flex: 1,
      backgroundColor: bg,
    },
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
      marginBottom: 25,
    },
    brand: {
      color: text,
      fontSize: 25,
      fontWeight: "800",
    },
    subtitle: {
      color: muted,
      fontSize: 12,
      marginTop: 3,
    },
    button: {
      paddingHorizontal: 15,
      paddingVertical: 12,
      borderRadius: 14,
      backgroundColor: surface,
      borderWidth: 1,
      borderColor: border,
      minHeight: 44,
      justifyContent: "center",
    },
    buttonText: {
      color: text,
      fontWeight: "700",
      fontSize: 13,
    },
    heading: {
      color: text,
      fontSize: 27,
      fontWeight: "800",
    },
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
    video: {
      width: "100%",
      height: "100%",
    },
    title: {
      color: text,
      fontSize: 17,
      fontWeight: "800",
    },
    muted: {
      color: muted,
      fontSize: 12,
      marginTop: 5,
    },
    primary: {
      backgroundColor: accent,
      borderRadius: 14,
      padding: 15,
      alignItems: "center",
      justifyContent: "center",
      minHeight: 48,
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
      marginBottom: 12,
    },
    timelineCard: {
      backgroundColor: surface,
      borderRadius: 20,
      borderWidth: 1,
      borderColor: border,
      padding: 16,
      marginBottom: 18,
    },
    timelineTrack: {
      height: 46,
      backgroundColor: dark ? "#303640" : "#E3E6EB",
      borderRadius: 10,
      overflow: "hidden",
      justifyContent: "center",
      marginTop: 14,
    },
    selectedRange: {
      position: "absolute",
      height: "100%",
      backgroundColor: dark ? "#AAB8C9" : "#64748B",
      opacity: 0.65,
    },
    playhead: {
      position: "absolute",
      width: 3,
      height: "100%",
      backgroundColor: "#FFFFFF",
    },
    timeRow: {
      flexDirection: "row",
      justifyContent: "space-between",
      marginTop: 12,
    },
    timeText: {
      color: muted,
      fontSize: 12,
      fontWeight: "600",
    },
    controls: {
      flexDirection: "row",
      flexWrap: "wrap",
      gap: 9,
      marginTop: 15,
    },
    controlButton: {
      flexGrow: 1,
      minWidth: 95,
      alignItems: "center",
      justifyContent: "center",
      padding: 12,
      borderRadius: 12,
      backgroundColor: dark ? "#292E35" : "#EDF0F4",
      minHeight: 46,
    },
    controlText: {
      color: text,
      fontSize: 12,
      fontWeight: "700",
    },
    footer: {
      color: muted,
      fontSize: 11,
      textAlign: "center",
      marginTop: 30,
    },
  });

  const progress = duration > 0 ? currentTime / duration : 0;
  const selectionLeft = duration > 0 ? (trimIn / duration) * 100 : 0;
  const selectionWidth =
    duration > 0 ? ((trimOut - trimIn) / duration) * 100 : 100;

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
            onPress={() => setDark((value) => !value)}
            accessibilityLabel="Ganti tema"
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

              <Pressable
                style={styles.primary}
                onPress={pickVideo}
                disabled={loading}
              >
                <Text style={styles.primaryText}>
                  {loading ? "Loading video..." : "＋ Import video"}
                </Text>
              </Pressable>
            </View>
          </>
        ) : (
          <>
            <View style={styles.header}>
              <Pressable style={styles.button} onPress={goHome}>
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
                {duration > 0
                  ? `${formatTime(duration)} total duration`
                  : "Loading video information..."}
              </Text>

              <Pressable
                style={styles.primary}
                onPress={togglePlayback}
                disabled={loading}
              >
                <Text style={styles.primaryText}>
                  {playing ? "Ⅱ  Pause" : "▶  Play"}
                </Text>
              </Pressable>
            </View>

            <Text style={styles.section}>Timeline</Text>

            <View style={styles.timelineCard}>
              <View style={styles.timeRow}>
                <Text style={styles.timeText}>
                  {formatTime(currentTime)}
                </Text>
                <Text style={styles.timeText}>
                  {formatTime(duration)}
                </Text>
              </View>

              <Pressable
                style={styles.timelineTrack}
                onLayout={(event) =>
                  setTimelineWidth(event.nativeEvent.layout.width)
                }
                onPress={(event) => {
                  if (!duration) return;
                  const position = event.nativeEvent.locationX;
                  seekTo((position / timelineWidth) * duration);
                }}
                accessibilityRole="adjustable"
                accessibilityLabel="Geser posisi video"
              >
                <View
                  style={[
                    styles.selectedRange,
                    {
                      left: `${selectionLeft}%`,
                      width: `${selectionWidth}%`,
                    },
                  ]}
                />
                <View
                  style={[
                    styles.playhead,
                    {
                      left: `${Math.min(100, Math.max(0, progress * 100))}%`,
                    },
                  ]}
                />
              </Pressable>

              <View style={styles.timeRow}>
                <Text style={styles.timeText}>
                  In: {formatTime(trimIn)}
                </Text>
                <Text style={styles.timeText}>
                  Out: {formatTime(trimOut)}
                </Text>
              </View>

              <View style={styles.controls}>
                <Pressable
                  style={styles.controlButton}
                  onPress={() => seekTo(currentTime - 5)}
                >
                  <Text style={styles.controlText}>↶  -5 sec</Text>
                </Pressable>

                <Pressable
                  style={styles.controlButton}
                  onPress={() => seekTo(currentTime + 5)}
                >
                  <Text style={styles.controlText}>+5 sec  ↷</Text>
                </Pressable>
              </View>

              <View style={styles.controls}>
                <Pressable
                  style={styles.controlButton}
                  onPress={markStart}
                >
                  <Text style={styles.controlText}>Set start</Text>
                </Pressable>

                <Pressable
                  style={styles.controlButton}
                  onPress={markEnd}
                >
                  <Text style={styles.controlText}>Set end</Text>
                </Pressable>
              </View>

              <Pressable
                style={styles.primary}
                onPress={previewSelection}
              >
                <Text style={styles.primaryText}>
                  ▶  Preview selected part
                </Text>
              </Pressable>

              <Text style={styles.muted}>
                Bagian terang menunjukkan rentang yang dipilih.
              </Text>
            </View>

            <Pressable
              style={styles.button}
              onPress={pickVideo}
              disabled={loading}
            >
              <Text style={styles.buttonText}>
                {loading ? "Loading..." : "＋ Replace video"}
              </Text>
            </Pressable>
          </>
        )}

        <Text style={styles.footer}>
          Vedit 1.0 · Create without limits.
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}