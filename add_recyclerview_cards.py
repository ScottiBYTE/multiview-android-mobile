from pathlib import Path

app_gradle = Path("app/build.gradle")
layout = Path("app/src/main/res/layout/activity_main.xml")
card = Path("app/src/main/res/layout/item_camera_card.xml")
main = Path("app/src/main/java/com/scottibyte/multiview/mobile/MainActivity.kt")

g = app_gradle.read_text()
if "androidx.recyclerview:recyclerview" not in g:
    g = g.replace(
        "implementation 'com.google.android.material:material:1.12.0'",
        "implementation 'com.google.android.material:material:1.12.0'\n    implementation 'androidx.recyclerview:recyclerview:1.3.2'"
    )
    app_gradle.write_text(g)

x = layout.read_text()
x = x.replace(
'''        <LinearLayout
            android:id="@+id/cameraList"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="18dp"
            android:orientation="vertical" />''',
'''        <androidx.recyclerview.widget.RecyclerView
            android:id="@+id/cameraRecycler"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="18dp"
            android:nestedScrollingEnabled="false" />'''
)
layout.write_text(x)

card.write_text('''<?xml version="1.0" encoding="utf-8"?>
<com.google.android.material.card.MaterialCardView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/cameraCard"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginBottom="14dp"
    app:cardBackgroundColor="@color/panel"
    app:cardCornerRadius="16dp"
    app:cardElevation="3dp"
    app:strokeColor="#334155"
    app:strokeWidth="1dp">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical">

        <FrameLayout
            android:layout_width="match_parent"
            android:layout_height="180dp"
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
                android:text="Thumbnail"
                android:textColor="#64748b"
                android:textSize="18sp"
                android:textStyle="bold" />
        </FrameLayout>

        <TextView
            android:id="@+id/cameraName"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:paddingStart="18dp"
            android:paddingTop="14dp"
            android:paddingEnd="18dp"
            android:textColor="@color/text_main"
            android:textSize="20sp"
            android:textStyle="bold" />

        <TextView
            android:id="@+id/cameraGroup"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:paddingStart="18dp"
            android:paddingTop="4dp"
            android:paddingEnd="18dp"
            android:paddingBottom="16dp"
            android:textColor="@color/text_muted"
            android:textSize="15sp" />

    </LinearLayout>
</com.google.android.material.card.MaterialCardView>
''')

k = main.read_text()

k = k.replace("import android.widget.LinearLayout\n", "")
k = k.replace("import android.widget.Toast", "import android.widget.Toast\nimport android.view.LayoutInflater\nimport android.view.View\nimport android.view.ViewGroup\nimport androidx.recyclerview.widget.LinearLayoutManager\nimport androidx.recyclerview.widget.RecyclerView")

k = k.replace(
"    private lateinit var cameraList: LinearLayout",
"    private lateinit var cameraRecycler: RecyclerView\n    private lateinit var cameraAdapter: CameraAdapter"
)

k = k.replace(
"        cameraList = findViewById(R.id.cameraList)",
'''        cameraRecycler = findViewById(R.id.cameraRecycler)
        cameraAdapter = CameraAdapter()
        cameraRecycler.layoutManager = LinearLayoutManager(this)
        cameraRecycler.adapter = cameraAdapter'''
)

old_render_start = k.find("    private fun renderCameraList(cameras: List<Camera>) {")
old_render_end = k.find("    private fun httpGetJson", old_render_start)
new_render = r'''    private fun renderCameraList(cameras: List<Camera>) {
        cameraAdapter.submit(cameras)
    }

    inner class CameraAdapter : RecyclerView.Adapter<CameraAdapter.CameraViewHolder>() {
        private val items = mutableListOf<Camera>()

        fun submit(cameras: List<Camera>) {
            items.clear()
            items.addAll(cameras)
            notifyDataSetChanged()
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CameraViewHolder {
            val view = LayoutInflater.from(parent.context)
                .inflate(R.layout.item_camera_card, parent, false)
            return CameraViewHolder(view)
        }

        override fun onBindViewHolder(holder: CameraViewHolder, position: Int) {
            val camera = items[position]
            holder.name.text = camera.name
            holder.group.text = camera.group.ifBlank { "Default" }
            holder.placeholder.visibility = View.VISIBLE
            holder.itemView.setOnClickListener {
                statusText.text = "Selected ${camera.name}"
            }
        }

        override fun getItemCount(): Int = items.size

        inner class CameraViewHolder(view: View) : RecyclerView.ViewHolder(view) {
            val name: TextView = view.findViewById(R.id.cameraName)
            val group: TextView = view.findViewById(R.id.cameraGroup)
            val placeholder: TextView = view.findViewById(R.id.thumbPlaceholder)
        }
    }

'''
if old_render_start == -1 or old_render_end == -1:
    raise SystemExit("Could not locate renderCameraList block.")
k = k[:old_render_start] + new_render + k[old_render_end:]

main.write_text(k)

print("Added RecyclerView camera cards.")
