from pathlib import Path

layout = Path("app/src/main/res/layout/activity_main.xml")
main = Path("app/src/main/java/com/scottibyte/multiview/mobile/MainActivity.kt")
card = Path("app/src/main/res/layout/item_camera_card.xml")

x = layout.read_text()

x = x.replace(
'''            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Connection"
                android:textColor="@color/text_main"
                android:textSize="18sp"
                android:textStyle="bold" />''',
'''            <Button
                android:id="@+id/connectionToggleButton"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Connection Settings" />

            <LinearLayout
                android:id="@+id/connectionDetails"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical">'''
)

x = x.replace(
'''            <TextView
                android:id="@+id/pairingHelpText"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="8dp"
                android:text=""
                android:textColor="@color/text_muted"
                android:textSize="15sp" />
        </LinearLayout>''',
'''            <TextView
                android:id="@+id/pairingHelpText"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="8dp"
                android:text=""
                android:textColor="@color/text_muted"
                android:textSize="15sp" />

            </LinearLayout>
        </LinearLayout>'''
)

layout.write_text(x)

c = card.read_text()
c = c.replace(
'android:text="Thumbnail"',
'android:text="No thumbnail yet"'
)
card.write_text(c)

k = main.read_text()

if "private lateinit var connectionDetails" not in k:
    k = k.replace(
        "    private lateinit var cameraHeaderText: TextView",
        "    private lateinit var cameraHeaderText: TextView\n    private lateinit var connectionDetails: View\n    private lateinit var connectionToggleButton: Button"
    )

k = k.replace(
'''        cameraHeaderText = findViewById(R.id.cameraHeaderText)''',
'''        cameraHeaderText = findViewById(R.id.cameraHeaderText)
        connectionDetails = findViewById(R.id.connectionDetails)
        connectionToggleButton = findViewById(R.id.connectionToggleButton)'''
)

k = k.replace(
'''        pairButton.setOnClickListener {
            requestPairing()
        }''',
'''        pairButton.setOnClickListener {
            requestPairing()
        }

        connectionToggleButton.setOnClickListener {
            connectionDetails.visibility = if (connectionDetails.visibility == View.VISIBLE) {
                View.GONE
            } else {
                View.VISIBLE
            }
        }'''
)

k = k.replace(
'''            connectionSummaryText.text = "Connected to: ${savedServer.removePrefix("https://").removePrefix("http://")}"
            statusText.text = "Stored pairing token found. Load cameras when ready."''',
'''            connectionSummaryText.text = "Connected to: ${savedServer.removePrefix("https://").removePrefix("http://")}"
            connectionDetails.visibility = View.GONE
            statusText.text = "Stored pairing token found. Load cameras when ready."'''
)

k = k.replace(
'''            connectionSummaryText.text = "Not paired"''',
'''            connectionSummaryText.text = "Not paired"
            connectionDetails.visibility = View.VISIBLE'''
)

k = k.replace(
'''                statusText.text = "Selected ${camera.name}"''',
'''                Toast.makeText(this@MainActivity, camera.name, Toast.LENGTH_SHORT).show()'''
)

main.write_text(k)

print("Added collapsible connection panel and cleaned card selection feedback.")
