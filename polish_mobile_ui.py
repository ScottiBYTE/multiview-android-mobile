from pathlib import Path

layout = Path("app/src/main/res/layout/activity_main.xml")
colors = Path("app/src/main/res/values/colors.xml")
main = Path("app/src/main/java/com/scottibyte/multiview/mobile/MainActivity.kt")

colors.write_text('''<resources>
    <color name="bg">#0f172a</color>
    <color name="panel">#172235</color>
    <color name="panel_soft">#111c2e</color>
    <color name="text_main">#f8fafc</color>
    <color name="text_muted">#cbd5e1</color>
    <color name="text_dim">#94a3b8</color>
    <color name="accent">#38bdf8</color>
</resources>
''')

layout.write_text('''<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/bg"
    android:fillViewport="true">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:paddingStart="20dp"
        android:paddingTop="42dp"
        android:paddingEnd="20dp"
        android:paddingBottom="22dp">

        <TextView
            android:id="@+id/titleText"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="ScottiBYTE MultiView"
            android:textColor="@color/text_main"
            android:textSize="28sp"
            android:textStyle="bold" />

        <TextView
            android:id="@+id/connectionSummaryText"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="6dp"
            android:text="Mobile camera viewer"
            android:textColor="@color/text_dim"
            android:textSize="15sp" />

        <TextView
            android:id="@+id/statusText"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="14dp"
            android:background="@color/panel_soft"
            android:padding="12dp"
            android:text="Ready."
            android:textColor="@color/accent"
            android:textSize="15sp"
            android:textStyle="bold" />

        <LinearLayout
            android:id="@+id/connectionPanel"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="18dp"
            android:orientation="vertical"
            android:background="@color/panel"
            android:padding="18dp">

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Connection"
                android:textColor="@color/text_main"
                android:textSize="18sp"
                android:textStyle="bold" />

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="12dp"
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

            <Button
                android:id="@+id/loadCamerasButton"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="10dp"
                android:text="Load Cameras" />

            <TextView
                android:id="@+id/pairingCodeText"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="18dp"
                android:text=""
                android:textColor="@color/accent"
                android:textSize="34sp"
                android:textStyle="bold" />

            <TextView
                android:id="@+id/pairingHelpText"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="8dp"
                android:text=""
                android:textColor="@color/text_muted"
                android:textSize="15sp" />
        </LinearLayout>

        <TextView
            android:id="@+id/cameraHeaderText"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="22dp"
            android:text="Cameras"
            android:textColor="@color/text_main"
            android:textSize="22sp"
            android:textStyle="bold" />

        <androidx.recyclerview.widget.RecyclerView
            android:id="@+id/cameraRecycler"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="14dp"
            android:nestedScrollingEnabled="false" />

    </LinearLayout>
</ScrollView>
''')

k = main.read_text()

if "private lateinit var connectionSummaryText" not in k:
    k = k.replace(
        "    private lateinit var statusText: TextView",
        "    private lateinit var statusText: TextView\n    private lateinit var connectionSummaryText: TextView\n    private lateinit var cameraHeaderText: TextView"
    )

k = k.replace(
    "        statusText = findViewById(R.id.statusText)",
    "        statusText = findViewById(R.id.statusText)\n        connectionSummaryText = findViewById(R.id.connectionSummaryText)\n        cameraHeaderText = findViewById(R.id.cameraHeaderText)"
)

k = k.replace(
    '''        val token = prefs().getString("token", null)
        if (!token.isNullOrBlank()) {
            statusText.text = "Stored pairing token found."
        }''',
    '''        val token = prefs().getString("token", null)
        if (!token.isNullOrBlank()) {
            connectionSummaryText.text = "Connected to: ${savedServer.removePrefix("https://").removePrefix("http://")}"
            statusText.text = "Stored pairing token found. Load cameras when ready."
        } else {
            connectionSummaryText.text = "Not paired"
        }'''
)

k = k.replace(
    '''                            statusText.text = "Paired successfully. Loading cameras..."''',
    '''                            connectionSummaryText.text = "Connected to: ${serverUrl.removePrefix("https://").removePrefix("http://")}"
                            statusText.text = "Paired successfully. Loading cameras..."'''
)

k = k.replace(
    '''                    renderCameraList(cameras)
                    statusText.text = "Loaded ${cameras.size} cameras."''',
    '''                    renderCameraList(cameras)
                    cameraHeaderText.text = "Cameras (${cameras.size})"
                    statusText.text = "Loaded ${cameras.size} cameras."'''
)

main.write_text(k)

print("Polished mobile UI layout and status/header text.")
