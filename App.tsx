
import React, { useState } from "react";
import {
  View,
  Text,
  ScrollView,
  Pressable,
  StyleSheet,
  SafeAreaView,
  StatusBar,
  useWindowDimensions,
  Alert,
} from "react-native";

export default function App() {
  const [dark, setDark] = useState(true);
  const { width } = useWindowDimensions();

  const bg = dark ? "#111316" : "#F4F5F7";
  const surface = dark ? "#1D2025" : "#FFFFFF";
  const text = dark ? "#F5F6F8" : "#17191D";
  const muted = dark ? "#9299A4" : "#777F8B";
  const border = dark ? "#30343B" : "#E5E7EB";
  const accent = dark ? "#DCE2EA" : "#252A32";

  const styles = StyleSheet.create({
    screen: { flex: 1, backgroundColor: bg },
    content: {
      paddingHorizontal: 22,
      paddingTop: 15,
      paddingBottom: 40,
      maxWidth: 700,
      width: "100%",
      alignSelf: "center",
    },
    header: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      marginBottom: 30,
    },
    logo: {
      width: 43,
      height: 43,
      borderRadius: 15,
      backgroundColor: accent,
      alignItems: "center",
      justifyContent: "center",
    },
    logoText: {
      color: dark ? "#15181D" : "#FFFFFF",
      fontSize: 24,
      fontWeight: "800",
    },
    brand: { fontSize: 23, fontWeight: "800", color: text },
    subtitle: { fontSize: 12, color: muted, marginTop: 3 },
    themeButton: {
      backgroundColor: surface,
      borderWidth: 1,
      borderColor: border,
      paddingHorizontal: 14,
      paddingVertical: 10,
      borderRadius: 20,
    },
    themeText: { color: text, fontSize: 12, fontWeight: "600" },
    heading: { color: text, fontSize: 29, fontWeight: "800", lineHeight: 36 },
    description: {
      color: muted,
      fontSize: 14,
      lineHeight: 21,
      marginTop: 8,
      marginBottom: 23,
    },
    createCard: {
      backgroundColor: surface,
      borderRadius: 25,
      padding: 21,
      borderWidth: 1,
      borderColor: border,
      marginBottom: 29,
    },
    createIcon: {
      width: 48,
      height: 48,
      borderRadius: 16,
      backgroundColor: dark ? "#343A43" : "#E9ECF1",
      alignItems: "center",
      justifyContent: "center",
      marginBottom: 17,
    },
    plus: { color: text, fontSize: 30, fontWeight: "300" },
    cardTitle: { color: text, fontSize: 19, fontWeight: "700" },
    cardDescription: {
      color: muted,
      fontSize: 13,
      lineHeight: 20,
      marginTop: 6,
      marginBottom: 17,
    },
    createButton: {
      backgroundColor: accent,
      padding: 15,
      borderRadius: 15,
      alignItems: "center",
    },
    createButtonText: {
      color: dark ? "#15181D" : "#FFFFFF",
      fontWeight: "700",
      fontSize: 14,
    },
    sectionHeader: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      marginBottom: 14,
    },
    sectionTitle: { color: text, fontSize: 18, fontWeight: "700" },
    sectionLink: { color: muted, fontSize: 12 },
    emptyCard: {
      backgroundColor: surface,
      borderRadius: 21,
      borderWidth: 1,
      borderColor: border,
      borderStyle: "dashed",
      padding: 24,
      alignItems: "center",
      marginBottom: 27,
    },
    emptyIcon: { fontSize: 29, marginBottom: 12 },
    emptyTitle: { color: text, fontSize: 15, fontWeight: "700" },
    emptyDescription: {
      color: muted,
      fontSize: 12,
      textAlign: "center",
      marginTop: 7,
      lineHeight: 19,
    },
    tools: {
      flexDirection: "row",
      gap: 11,
      marginTop: 14,
    },
    tool: {
      flex: 1,
      backgroundColor: surface,
      borderRadius: 19,
      borderWidth: 1,
      borderColor: border,
      padding: 15,
      minHeight: 105,
      justifyContent: "space-between",
    },
    toolIcon: { fontSize: 22 },
    toolName: { color: text, fontSize: 13, fontWeight: "700" },
    toolDesc: { color: muted, fontSize: 10, marginTop: 4 },
    footer: {
      marginTop: 32,
      alignItems: "center",
    },
    footerText: { color: muted, fontSize: 11 },
  });

  const notify = (title: string) =>
    Alert.alert(title, "Fitur ini akan tersedia dalam pengembangan Vedit berikutnya.");

  return (
    <SafeAreaView style={styles.screen}>
      <StatusBar barStyle={dark ? "light-content" : "dark-content"} backgroundColor={bg} />

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 11 }}>
            <View style={styles.logo}>
              <Text style={styles.logoText}>V</Text>
            </View>
            <View>
              <Text style={styles.brand}>Vedit</Text>
              <Text style={styles.subtitle}>Create without limits.</Text>
            </View>
          </View>

          <Pressable
            style={styles.themeButton}
            onPress={() => setDark(!dark)}
          >
            <Text style={styles.themeText}>
              {dark ? "☀  Light" : "☾  Dark"}
            </Text>
          </Pressable>
        </View>

        <Text style={styles.heading}>
          Make something{"\n"}amazing.
        </Text>
        <Text style={styles.description}>
          Your creative space. Turn your moments into something memorable.
        </Text>

        <View style={styles.createCard}>
          <View style={styles.createIcon}>
            <Text style={styles.plus}>＋</Text>
          </View>
          <Text style={styles.cardTitle}>Start a new project</Text>
          <Text style={styles.cardDescription}>
            Bring your videos and photos together. Your next creation starts here.
          </Text>
          <Pressable
            style={styles.createButton}
            onPress={() => notify("New Project")}
          >
            <Text style={styles.createButtonText}>＋   Create project</Text>
          </Pressable>
        </View>

        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Recent projects</Text>
          <Text style={styles.sectionLink}>Your workspace</Text>
        </View>

        <View style={styles.emptyCard}>
          <Text style={styles.emptyIcon}>▧</Text>
          <Text style={styles.emptyTitle}>Nothing here yet</Text>
          <Text style={styles.emptyDescription}>
            Your saved editing projects will appear here.{"\n"}
            Start creating your first video!
          </Text>
        </View>

        <Text style={styles.sectionTitle}>Explore</Text>

        <View style={styles.tools}>
          <Pressable style={styles.tool} onPress={() => notify("Templates")}>
            <Text style={styles.toolIcon}>▤</Text>
            <View>
              <Text style={styles.toolName}>Templates</Text>
              <Text style={styles.toolDesc}>Creative ideas</Text>
            </View>
          </Pressable>

          <Pressable style={styles.tool} onPress={() => notify("Settings")}>
            <Text style={styles.toolIcon}>⚙</Text>
            <View>
              <Text style={styles.toolName}>Settings</Text>
              <Text style={styles.toolDesc}>Customize Vedit</Text>
            </View>
          </Pressable>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>Vedit 1.0 · Made for creators</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
