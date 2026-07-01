from pathlib import Path

app_gradle = Path("app/build.gradle")
manifest = Path("app/src/main/AndroidManifest.xml")
layout = Path("app/src/main/res/layout/activity_player.xml")
main = Path("app/src/main/java/com/scottibyte/multiview/mobile/MainActivity.kt")
player = Path("app/src/main/java/com/scottibyte/multiview/mobile/PlayerActivity.kt")

g = app_gradle.read_text()
if "androidx.media3:media3-exoplayer" not in g:
    g = g.replace(
        "implementation 'io.coil-kt:coil:2.7.0'",
        "implementation 'io.coil-kt:coil:2.7.0'\n    implementation 'androidx.media3:media3-exoplayer:1.5.1'\n    implementation 'androidx.media3:media3-ui:1.5.1'"
    )
app_gradle.write_text(g)

m = manifest.read_text()
if 'android:name=".PlayerActivity"' not in m:
    m = m.replace(
'''        <activity
            android:name=".MainActivity"
            android:exported="true">''',
'''        <activity
            android:name=".PlayerActivity"
            android:exported="false"
            android:screenOrientation="landscape" />

        <activity
            android:name=".MainActivity"
            android:exported="true">'''
    )
manifest.write_text(m)

layout.write_text('''<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#000000">

    <androidx.media3.ui.PlayerView
        android:id="@+id/playerView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        app:show_buffering="when_playing"
        app:use_controller="true" />

    <TextView
        android:id="@+id/playerTitle"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="top|start"
        android:layout_margin="18dp"
        android:background="#99000000"
        android:paddingStart="14dp"
        android:paddingTop="8dp"
        android:paddingEnd="14dp"
        android:paddingBottom="8dp"
        android:textColor="#ffffff"
        android:textSize="18sp"
        android:textStyle="bold" />

</FrameLayout>
''')

player.write_text('''package com.scottibyte.multiview.mobile

import android.app.Activity
import android.os.Bundle
import android.view.WindowManager
import android.widget.TextView
import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView

class PlayerActivity : Activity() {
    private var player: ExoPlayer? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        setContentView(R.layout.activity_player)

        val cameraName = intent.getStringExtra("cameraName") ?: "Camera"
        val streamUrl = intent.getStringExtra("streamUrl") ?: ""

        findViewById<TextView>(R.id.playerTitle).text = cameraName

        val playerView = findViewById<PlayerView>(R.id.playerView)
        player = ExoPlayer.Builder(this).build().also { exo ->
            playerView.player = exo
            exo.setMediaItem(MediaItem.fromUri(streamUrl))
            exo.prepare()
            exo.playWhenReady = true
        }
    }

    override fun onStop() {
        super.onStop()
        player?.release()
        player = null
    }
}
''')

k = main.read_text()

if "import android.content.Intent" not in k:
    k = k.replace("import android.app.Activity", "import android.app.Activity\nimport android.content.Intent")

k = k.replace(
'''            holder.itemView.setOnClickListener {
                Toast.makeText(this@MainActivity, camera.name, Toast.LENGTH_SHORT).show()
            }''',
'''            holder.itemView.setOnClickListener {
                val intent = Intent(this@MainActivity, PlayerActivity::class.java)
                    .putExtra("cameraId", camera.id)
                    .putExtra("cameraName", camera.name)
                    .putExtra("cameraGroup", camera.group)
                    .putExtra("streamUrl", camera.hlsUrl)
                    .putExtra("thumbnailUrl", camera.thumbnailUrl)
                startActivity(intent)
            }'''
)

main.write_text(k)

print("Added single-camera landscape PlayerActivity.")
