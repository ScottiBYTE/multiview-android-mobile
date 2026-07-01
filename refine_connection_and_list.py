from pathlib import Path

layout = Path("app/src/main/res/layout/activity_main.xml")
main = Path("app/src/main/java/com/scottibyte/multiview/mobile/MainActivity.kt")
drawable_dir = Path("app/src/main/res/drawable")
drawable_dir.mkdir(parents=True, exist_ok=True)

(drawable_dir / "connection_button_bg.xml").write_text('''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <gradient
        android:startColor="#38bdf8"
        android:endColor="#2563eb"
        android:angle="0" />
    <corners android:radius="28dp" />
    <padding
        android:left="18dp"
        android:right="18dp"
        android:top="8dp"
        android:bottom="8dp" />
</shape>
''')

x = layout.read_text()

x = x.replace(
'''<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/bg"
    android:fillViewport="true">

    <LinearLayout''',
'''<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/bg"
    android:orientation="vertical">

    <LinearLayout'''
)

x = x.replace(
'''        android:layout_height="wrap_content"''',
'''        android:layout_height="wrap_content"''',
1
)

x = x.replace(
'''                android:paddingBottom="8dp"
                android:text="Connection Settings" />''',
'''                android:paddingBottom="8dp"
                android:background="@drawable/connection_button_bg"
                android:textColor="#ffffff"
                android:textAllCaps="false"
                android:text="Connection Settings" />'''
)

x = x.replace(
'''        <androidx.recyclerview.widget.RecyclerView
            android:id="@+id/cameraRecycler"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="14dp"
            android:nestedScrollingEnabled="false" />

    </LinearLayout>
</ScrollView>
''',
'''        <androidx.recyclerview.widget.RecyclerView
            android:id="@+id/cameraRecycler"
            android:layout_width="match_parent"
            android:layout_height="0dp"
            android:layout_weight="1"
            android:layout_marginTop="14dp" />

    </LinearLayout>
</LinearLayout>
'''
)

layout.write_text(x)

k = main.read_text()

k = k.replace(
'''        pairButton.setOnClickListener {
            requestPairing()
        }''',
'''        pairButton.setOnClickListener {
            if (prefs().getString("token", null).isNullOrBlank()) {
                requestPairing()
            } else {
                resetPairing()
            }
        }'''
)

k = k.replace(
'''            connectionDetails.visibility = View.GONE
            statusText.text = "Stored pairing token found. Loading cameras..."
            fetchConfig()''',
'''            connectionDetails.visibility = View.GONE
            pairButton.text = "Reset Pairing"
            statusText.text = "Stored pairing token found. Loading cameras..."
            fetchConfig()'''
)

k = k.replace(
'''            connectionDetails.visibility = View.VISIBLE''',
'''            connectionDetails.visibility = View.VISIBLE
            pairButton.text = "Pair With Server"'''
)

k = k.replace(
'''                            connectionDetails.visibility = View.GONE
                            statusText.text = "Paired successfully. Loading cameras..."''',
'''                            connectionDetails.visibility = View.GONE
                            pairButton.text = "Reset Pairing"
                            statusText.text = "Paired successfully. Loading cameras..."'''
)

insert = r'''
    private fun resetPairing() {
        pollingCode = null
        prefs().edit().remove("token").apply()
        pairButton.text = "Pair With Server"
        connectionStateText.text = "Connection status: Not paired"
        connectionDetails.visibility = View.VISIBLE
        cameraAdapter.submit(emptyList())
        cameraHeaderText.text = "Cameras"
        statusText.text = "Pairing reset. Pair with the server again."
        Toast.makeText(this, "Pairing reset", Toast.LENGTH_SHORT).show()
    }

'''
marker = "    private fun fetchConfig()"
if "private fun resetPairing()" not in k:
    k = k.replace(marker, insert + marker)

main.write_text(k)

print("Refined connection bubble, reset pairing behavior, and RecyclerView scrolling.")
