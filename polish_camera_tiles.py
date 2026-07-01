from pathlib import Path

layout = Path("app/src/main/res/layout/activity_main.xml")
tile = Path("app/src/main/res/layout/item_camera_card.xml")
main = Path("app/src/main/java/com/scottibyte/multiview/mobile/MainActivity.kt")

x = layout.read_text()
x = x.replace(
'''            <Button
                android:id="@+id/loadCamerasButton"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="10dp"
                android:text="Load Cameras" />
''',
''
)
layout.write_text(x)

tile.write_text('''<?xml version="1.0" encoding="utf-8"?>
<com.google.android.material.card.MaterialCardView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/cameraCard"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginBottom="16dp"
    app:cardBackgroundColor="@color/panel"
    app:cardCornerRadius="18dp"
    app:cardElevation="4dp"
    app:strokeColor="#334155"
    app:strokeWidth="1dp">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical">

        <FrameLayout
            android:layout_width="match_parent"
            android:layout_height="194dp"
            android:background="#020617">

            <ImageView
                android:id="@+id/cameraThumb"
                android:layout_width="match_parent"
                android:layout_height="match_parent"
                android:contentDescription="Camera thumbnail"
                android:scaleType="centerCrop" />

            <TextView
                android:id="@+id/thumbPlaceholder"
                android:layout_width="match_parent"
                android:layout_height="match_parent"
                android:gravity="center"
                android:text=""
                android:textColor="#64748b"
                android:textSize="16sp" />
        </FrameLayout>

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:paddingStart="18dp"
            android:paddingTop="14dp"
            android:paddingEnd="18dp"
            android:paddingBottom="16dp">

            <TextView
                android:id="@+id/cameraName"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:textColor="@color/text_main"
                android:textSize="21sp"
                android:textStyle="bold" />

            <TextView
                android:id="@+id/cameraGroup"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="3dp"
                android:textColor="@color/text_muted"
                android:textSize="15sp" />

            <TextView
                android:id="@+id/cameraState"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="10dp"
                android:text="● Online"
                android:textColor="@color/accent"
                android:textSize="14sp"
                android:textStyle="bold" />

        </LinearLayout>

    </LinearLayout>
</com.google.android.material.card.MaterialCardView>
''')

k = main.read_text()

k = k.replace(
'''        findViewById<Button>(R.id.loadCamerasButton).setOnClickListener {
            fetchConfig()
        }
''',
''
)

k = k.replace(
'''            val placeholder: TextView = view.findViewById(R.id.thumbPlaceholder)''',
'''            val placeholder: TextView = view.findViewById(R.id.thumbPlaceholder)
            val state: TextView = view.findViewById(R.id.cameraState)'''
)

main.write_text(k)

print("Polished camera tiles and removed Load Cameras button.")
