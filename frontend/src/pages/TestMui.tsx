import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";

export default function TestMui() {
    return (
        <div style={{ padding: 40 }}>
            <Typography variant="h4" gutterBottom>
                ✅ MUI работает!
            </Typography>
            <Button variant="contained" color="primary">
                Кнопка MUI
            </Button>
        </div>
    );
}
