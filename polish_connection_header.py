from pathlib import Path

layout = Path("app/src/main/res/layout/activity_main.xml")
main = Path("app/src/main/java/com/scottibyte/multiview/mobile/MainActivity.kt")

x = layout.read_text()

x = x.replace(
    'android:text="Mobile camera viewer"',
    'android:text="Camera viewer"'
)

x = x.replace(
'''            <Button
                android:id="@+id/connectionToggleButton"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Connection Settings" />''',
'''            <Button
                android:id="@+id/connectionToggleButton"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:minHeight="0dp"
                android:paddingStart="18dp"
                android:paddingTop="8dp"
                android:paddingEnd="18dp"
                android:paddingBottom="8dp"
                android:text="Connection Settings" />'''
)

x = x.replace(
'''            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="12dp"
                android:text="Server URL"''',
'''            <TextView
                android:id="@+id/connectionStateText"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="12dp"
                android:text="Connection status: Not paired"
                android:textColor="@color/accent"
                android:textStyle="bold" />

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="12dp"
                android:text="Server URL"'''
)

layout.write_text(x)

k = main.read_text()

k = k.replace(
    "    private lateinit var connectionToggleButton: Button",
    "    private lateinit var connectionToggleButton: Button\n    private lateinit var connectionStateText: TextView"
)

k = k.replace(
    "        connectionToggleButton = findViewById(R.id.connectionToggleButton)",
    "        connectionToggleButton = findViewById(R.id.connectionToggleButton)\n        connectionStateText = findViewById(R.id.connectionStateText)"
)

k = k.replace(
    '''connectionSummaryText.text = "Connected to: ${savedServer.removePrefix("https://").removePrefix("http://")}"''',
    '''connectionSummaryText.text = "Camera viewer"
            connectionStateText.text = "Connection status: Connected"'''
)

k = k.replace(
    '''connectionSummaryText.text = "Not paired"''',
    '''connectionSummaryText.text = "Camera viewer"
            connectionStateText.text = "Connection status: Not paired"'''
)

k = k.replace(
    '''connectionSummaryText.text = "Connected to: ${serverUrl.removePrefix("https://").removePrefix("http://")}"''',
    '''connectionSummaryText.text = "Camera viewer"
                            connectionStateText.text = "Connection status: Connected"'''
)

main.write_text(k)

print("Polished connection header and moved connection status into details.")
