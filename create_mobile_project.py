from pathlib import Path

root = Path.cwd()
pkg_path = root / "app/src/main/java/com/scottibyte/multiview/mobile"
res_layout = root / "app/src/main/res/layout"
res_values = root / "app/src/main/res/values"

for p in [pkg_path, res_layout, res_values]:
    p.mkdir(parents=True, exist_ok=True)

(root / "settings.gradle").write_text('''pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "ScottiBYTE MultiView Mobile"
include ':app'
''')

(root / "build.gradle").write_text('''plugins {
    id 'com.android.application' version '8.7.3' apply false
    id 'org.jetbrains.kotlin.android' version '2.0.21' apply false
}
''')

(root / "app/build.gradle").write_text('''plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}

android {
    namespace 'com.scottibyte.multiview.mobile'
    compileSdk 35

    defaultConfig {
        applicationId 'com.scottibyte.multiview.mobile'
        minSdk 26
        targetSdk 35
        versionCode 1
        versionName '0.1.0'
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.15.0'
    implementation 'androidx.appcompat:appcompat:1.7.0'
    implementation 'com.google.android.material:material:1.12.0'
}
''')

(root / "app/src/main/AndroidManifest.xml").write_text('''<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:theme="@style/AppTheme"
        android:label="ScottiBYTE MultiView Mobile"
        android:allowBackup="true"
        android:supportsRtl="true">

        <activity
            android:name=".MainActivity"
            android:exported="true">

            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>

        </activity>
    </application>
</manifest>
''')

(res_values / "colors.xml").write_text('''<resources>
    <color name="bg">#0f172a</color>
    <color name="panel">#172235</color>
    <color name="text_main">#f8fafc</color>
    <color name="text_muted">#cbd5e1</color>
    <color name="accent">#38bdf8</color>
</resources>
''')

(res_values / "styles.xml").write_text('''<resources>
    <style name="AppTheme" parent="Theme.MaterialComponents.DayNight.NoActionBar">
        <item name="android:fontFamily">sans</item>
        <item name="android:windowLightStatusBar">false</item>
        <item name="android:navigationBarColor">@color/bg</item>
        <item name="android:statusBarColor">@color/bg</item>
        <item name="colorPrimary">@color/accent</item>
        <item name="colorPrimaryVariant">@color/panel</item>
        <item name="colorOnPrimary">@color/bg</item>
    </style>
</resources>
''')

(res_layout / "activity_main.xml").write_text('''<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/bg"
    android:fillViewport="true">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="22dp">

        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="ScottiBYTE MultiView Mobile"
            android:textColor="@color/text_main"
            android:textSize="26sp"
            android:textStyle="bold" />

        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="6dp"
            android:text="Phone and tablet client for ScottiBYTE MultiView Server"
            android:textColor="@color/text_muted"
            android:textSize="15sp" />

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="24dp"
            android:orientation="vertical"
            android:background="@color/panel"
            android:padding="18dp">

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Server URL"
                android:textColor="@color/text_muted"
                android:textStyle="bold" />

            <EditText
                android:id="@+id/serverUrlEdit"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="8dp"
                android:hint="https://multiview-server.scottibyte.com"
                android:inputType="textUri"
                android:singleLine="true"
                android:text="https://multiview-server.scottibyte.com"
                android:textColor="@color/text_main"
                android:textColorHint="#64748b" />

            <Button
                android:id="@+id/saveServerButton"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="14dp"
                android:text="Save Server URL" />

            <Button
                android:id="@+id/pairButton"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="10dp"
                android:text="Pair With Server" />

            <TextView
                android:id="@+id/statusText"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="18dp"
                android:text="Ready."
                android:textColor="@color/accent"
                android:textSize="18sp"
                android:textStyle="bold" />
        </LinearLayout>

    </LinearLayout>
</ScrollView>
''')

(pkg_path / "MainActivity.kt").write_text('''package com.scottibyte.multiview.mobile

import android.app.Activity
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast

class MainActivity : Activity() {
    private val defaultServerUrl = "https://multiview-server.scottibyte.com"

    private lateinit var serverUrlEdit: EditText
    private lateinit var statusText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        serverUrlEdit = findViewById(R.id.serverUrlEdit)
        statusText = findViewById(R.id.statusText)

        val savedServer = getPreferences(MODE_PRIVATE)
            .getString("serverUrl", defaultServerUrl) ?: defaultServerUrl

        serverUrlEdit.setText(savedServer)

        findViewById<Button>(R.id.saveServerButton).setOnClickListener {
            val value = serverUrlEdit.text.toString().trim().trimEnd('/').ifBlank { defaultServerUrl }
            getPreferences(MODE_PRIVATE).edit().putString("serverUrl", value).apply()
            serverUrlEdit.setText(value)
            statusText.text = "Server URL saved."
            Toast.makeText(this, "Server URL saved", Toast.LENGTH_SHORT).show()
        }

        findViewById<Button>(R.id.pairButton).setOnClickListener {
            val value = serverUrlEdit.text.toString().trim().trimEnd('/').ifBlank { defaultServerUrl }
            statusText.text = "Pairing will use: $value"
        }
    }
}
''')

(root / ".gitignore").write_text('''.gradle/
build/
app/build/
local.properties
*.iml
.idea/
''')

print("Created ScottiBYTE MultiView Mobile Android project skeleton.")
print("Next: ./gradlew assembleDebug")
