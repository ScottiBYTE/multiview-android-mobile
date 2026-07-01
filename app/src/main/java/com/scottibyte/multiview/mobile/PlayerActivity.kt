package com.scottibyte.multiview.mobile

import android.app.Activity
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.view.WindowManager
import android.widget.TextView
import androidx.media3.common.MediaItem
import androidx.media3.common.Player
import androidx.media3.datasource.DefaultHttpDataSource
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.source.DefaultMediaSourceFactory
import androidx.media3.ui.PlayerView

class PlayerActivity : Activity() {
    private var player: ExoPlayer? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        setContentView(R.layout.activity_player)

        val cameraName = intent.getStringExtra("cameraName") ?: "Camera"
        val streamUrl = intent.getStringExtra("streamUrl") ?: ""
        Log.d("MultiViewPlayer", "camera=$cameraName streamUrl=$streamUrl")

        val title = findViewById<TextView>(R.id.playerTitle)
        title.text = "$cameraName\nLoading..."

        if (streamUrl.isBlank()) {
            title.text = "$cameraName\nNo stream URL"
            return
        }

        val playerView = findViewById<PlayerView>(R.id.playerView)

        val exo = makePlayer()
        player = exo

        playerView.useController = false
        playerView.player = exo

        exo.addListener(object : Player.Listener {
            override fun onPlaybackStateChanged(state: Int) {
                Log.d("MultiViewPlayer", "state=$state camera=$cameraName")
                title.text = when (state) {
                    Player.STATE_BUFFERING -> "$cameraName\nBuffering..."
                    Player.STATE_READY -> "$cameraName\nPlaying"
                    Player.STATE_ENDED -> "$cameraName\nEnded"
                    Player.STATE_IDLE -> "$cameraName\nIdle"
                    else -> "$cameraName\nState: $state"
                }
            }

            override fun onPlayerError(error: androidx.media3.common.PlaybackException) {
                Log.e("MultiViewPlayer", "player error ${error.errorCodeName}: ${error.message}", error)
                title.text = "$cameraName\nPlayback error: ${error.errorCodeName}"
            }
        })

        exo.setMediaItem(MediaItem.fromUri(Uri.parse(streamUrl)))
        exo.prepare()
        exo.playWhenReady = true
    }

    private fun makePlayer(): ExoPlayer {
        val httpDataSourceFactory = DefaultHttpDataSource.Factory()
        val mediaSourceFactory = DefaultMediaSourceFactory(this)
            .setDataSourceFactory(httpDataSourceFactory)

        return ExoPlayer.Builder(this)
            .setMediaSourceFactory(mediaSourceFactory)
            .build()
    }

    override fun onStop() {
        super.onStop()
        player?.release()
        player = null
    }
}
