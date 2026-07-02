package com.scottibyte.multiview.mobile

import android.app.Activity
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.GestureDetector
import android.view.MotionEvent
import android.view.ScaleGestureDetector
import android.view.View
import android.view.WindowInsets
import android.view.WindowInsetsController
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
    private lateinit var playerView: PlayerView
    private lateinit var title: TextView
    private lateinit var backButton: TextView

    private val handler = Handler(Looper.getMainLooper())
    private lateinit var gestureDetector: GestureDetector
    private lateinit var scaleGestureDetector: ScaleGestureDetector
    private var zoomScale = 1.0f
    private var panX = 0f
    private var panY = 0f
    private var lastTouchX = 0f
    private var lastTouchY = 0f

    private var cameraIndex = 0
    private var cameraNames = arrayListOf<String>()
    private var cameraGroups = arrayListOf<String>()
    private var cameraUrls = arrayListOf<String>()

    private val hideOverlayRunnable = Runnable {
        title.visibility = View.GONE
        backButton.visibility = View.GONE
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        setContentView(R.layout.activity_player)
        enterImmersiveMode()

        playerView = findViewById(R.id.playerView)
        title = findViewById(R.id.playerTitle)
        backButton = findViewById(R.id.backButton)
        backButton.setOnClickListener { finish() }

        cameraIndex = intent.getIntExtra("cameraIndex", 0)
        cameraNames = intent.getStringArrayListExtra("cameraNames") ?: arrayListOf()
        cameraGroups = intent.getStringArrayListExtra("cameraGroups") ?: arrayListOf()
        cameraUrls = intent.getStringArrayListExtra("cameraUrls") ?: arrayListOf()

        if (cameraUrls.isEmpty()) {
            title.text = "No cameras available"
            return
        }

        if (cameraIndex !in cameraUrls.indices) {
            cameraIndex = 0
        }

        player = makePlayer()
        playerView.useController = false
        playerView.player = player

        player?.addListener(object : Player.Listener {
            override fun onPlaybackStateChanged(state: Int) {
                val name = currentName()
                title.text = when (state) {
                    Player.STATE_BUFFERING -> "$name\nBuffering..."
                    Player.STATE_READY -> name
                    Player.STATE_ENDED -> "$name\nEnded"
                    Player.STATE_IDLE -> "$name\nIdle"
                    else -> "$name\nState: $state"
                }

                if (state == Player.STATE_READY) {
                    scheduleOverlayHide()
                } else {
                    showOverlay()
                }
            }

            override fun onPlayerError(error: androidx.media3.common.PlaybackException) {
                Log.e("MultiViewPlayer", "player error ${error.errorCodeName}: ${error.message}", error)
                title.text = "${currentName()}\nPlayback error: ${error.errorCodeName}"
                showOverlay()
            }
        })

        scaleGestureDetector = ScaleGestureDetector(this, object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
            override fun onScale(detector: ScaleGestureDetector): Boolean {
                zoomScale *= detector.scaleFactor
                zoomScale = zoomScale.coerceIn(1.0f, 4.0f)

                applyZoomPan()

                showOverlay()
                scheduleOverlayHide()
                return true
            }
        })

        gestureDetector = GestureDetector(this, object : GestureDetector.SimpleOnGestureListener() {
            override fun onSingleTapConfirmed(e: MotionEvent): Boolean {
                toggleOverlay()
                return true
            }

            override fun onFling(
                e1: MotionEvent?,
                e2: MotionEvent,
                velocityX: Float,
                velocityY: Float
            ): Boolean {
                val startX = e1?.x ?: return false
                val dx = e2.x - startX

                if (zoomScale <= 1.05f && kotlin.math.abs(dx) > 120 && kotlin.math.abs(velocityX) > 250) {
                    if (dx < 0) {
                        playNext()
                    } else {
                        playPrevious()
                    }
                    return true
                }

                return false
            }
        })

        playerView.setOnTouchListener { _, event ->
            scaleGestureDetector.onTouchEvent(event)

            if (scaleGestureDetector.isInProgress) {
                return@setOnTouchListener true
            }

            if (zoomScale > 1.0f) {
                when (event.actionMasked) {
                    MotionEvent.ACTION_DOWN -> {
                        lastTouchX = event.x
                        lastTouchY = event.y
                    }
                    MotionEvent.ACTION_MOVE -> {
                        val dx = event.x - lastTouchX
                        val dy = event.y - lastTouchY

                        panX += dx
                        panY += dy

                        val maxPanX = (playerView.width * (zoomScale - 1f)) / 2f
                        val maxPanY = (playerView.height * (zoomScale - 1f)) / 2f

                        panX = panX.coerceIn(-maxPanX, maxPanX)
                        panY = panY.coerceIn(-maxPanY, maxPanY)

                        lastTouchX = event.x
                        lastTouchY = event.y

                        applyZoomPan()
                    }
                }
                gestureDetector.onTouchEvent(event)
                return@setOnTouchListener true
            }

            gestureDetector.onTouchEvent(event)
            true
        }

        playCamera(cameraIndex)
    }


    private fun enterImmersiveMode() {
        window.insetsController?.let { controller ->
            controller.hide(WindowInsets.Type.statusBars() or WindowInsets.Type.navigationBars())
            controller.systemBarsBehavior =
                WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        }
    }

    private fun makePlayer(): ExoPlayer {
        val httpDataSourceFactory = DefaultHttpDataSource.Factory()
        val mediaSourceFactory = DefaultMediaSourceFactory(this)
            .setDataSourceFactory(httpDataSourceFactory)

        return ExoPlayer.Builder(this)
            .setMediaSourceFactory(mediaSourceFactory)
            .build()
    }


    private fun applyZoomPan() {
        playerView.scaleX = zoomScale
        playerView.scaleY = zoomScale
        playerView.translationX = panX
        playerView.translationY = panY
    }

    private fun resetZoomPan() {
        zoomScale = 1.0f
        panX = 0f
        panY = 0f
        applyZoomPan()
    }

    private fun playCamera(index: Int) {
        if (index !in cameraUrls.indices) return

        cameraIndex = index
        resetZoomPan()
        val name = currentName()
        val url = cameraUrls[index]

        Log.d("MultiViewPlayer", "camera=$name streamUrl=$url")

        title.text = "$name\nLoading..."
        showOverlay()

        player?.stop()
        player?.clearMediaItems()
        player?.setMediaItem(MediaItem.fromUri(Uri.parse(url)))
        player?.prepare()
        player?.playWhenReady = true
    }

    private fun playNext() {
        val next = (cameraIndex + 1) % cameraUrls.size
        playCamera(next)
    }

    private fun playPrevious() {
        val previous = (cameraIndex - 1 + cameraUrls.size) % cameraUrls.size
        playCamera(previous)
    }

    private fun currentName(): String {
        return cameraNames.getOrNull(cameraIndex) ?: "Camera"
    }

    private fun showOverlay() {
        title.visibility = View.VISIBLE
        backButton.visibility = View.VISIBLE
        handler.removeCallbacks(hideOverlayRunnable)
    }

    private fun scheduleOverlayHide() {
        handler.removeCallbacks(hideOverlayRunnable)
        handler.postDelayed(hideOverlayRunnable, 2500)
    }

    private fun toggleOverlay() {
        if (title.visibility == View.VISIBLE) {
            title.visibility = View.GONE
        backButton.visibility = View.GONE
            handler.removeCallbacks(hideOverlayRunnable)
        } else {
            showOverlay()
            scheduleOverlayHide()
        }
    }

    override fun onStop() {
        super.onStop()
        handler.removeCallbacks(hideOverlayRunnable)
        player?.release()
        player = null
    }
}
