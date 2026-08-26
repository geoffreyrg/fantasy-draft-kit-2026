"""
Configuration and settings management for Fantasy Football Draft Kit 2026.
Supports .env loading with graceful fallbacks and strongly typed settings.
"""

from dataclasses import dataclass, field
from pathlib import Path
import os
from dotenv import load_dotenv

# Base directory for the project
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env file from PROJECT_ROOT or config/
env_paths = [
    PROJECT_ROOT / ".env",
    PROJECT_ROOT / "config" / ".env",
]
for p in env_paths:
    if p.exists():
        load_dotenv(dotenv_path=p, override=False)


@dataclass
class ApiCredentials:
    fantasypros_api_key: str = field(default_factory=lambda: os.getenv("FANTASYPROS_API_KEY", ""))
    fantasypros_base_url: str = field(
        default_factory=lambda: os.getenv("FANTASYPROS_BASE_URL", "https://api.fantasypros.com/public/v2/json")
    )
    reddit_client_id: str = field(default_factory=lambda: os.getenv("REDDIT_CLIENT_ID", ""))
    reddit_client_secret: str = field(default_factory=lambda: os.getenv("REDDIT_CLIENT_SECRET", ""))
    reddit_user_agent: str = field(default_factory=lambda: os.getenv("REDDIT_USER_AGENT", "FantasyFootballAgent/1.0"))
    google_service_account_json: str = field(
        default_factory=lambda: os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "config/google_service_account.json")
    )
    google_sheet_id: str = field(default_factory=lambda: os.getenv("GOOGLE_SHEET_ID", ""))
    google_sheet_name: str = field(
        default_factory=lambda: os.getenv("GOOGLE_SHEET_NAME", "Fantasy Draft Kit 2026 Master Board")
    )

    @property
    def has_fantasypros(self) -> bool:
        return bool(self.fantasypros_api_key and self.fantasypros_api_key.strip())

    @property
    def has_reddit(self) -> bool:
        return bool(self.reddit_client_id and self.reddit_client_secret)

    @property
    def has_google_sheets(self) -> bool:
        path = PROJECT_ROOT / self.google_service_account_json if not os.path.isabs(self.google_service_account_json) else Path(self.google_service_account_json)
        return path.exists() and bool(self.google_sheet_id)


@dataclass
class PathConfig:
    root_dir: Path = PROJECT_ROOT
    data_dir: Path = PROJECT_ROOT / "data"
    raw_data_dir: Path = PROJECT_ROOT / "data" / "raw"
    processed_data_dir: Path = PROJECT_ROOT / "data" / "processed"
    export_data_dir: Path = PROJECT_ROOT / "data" / "export"
    config_dir: Path = PROJECT_ROOT / "config"
    src_dir: Path = PROJECT_ROOT / "src"

    # Specific file targets
    pdf_guide_path: Path = PROJECT_ROOT / "data" / "raw" / "Joel Smyth's Draft Guide 2026.pdf"
    duracell_csv_path: Path = PROJECT_ROOT / "data" / "raw" / "duracell_rankings.csv"
    master_csv_path: Path = PROJECT_ROOT / "data" / "export" / "master_draft_kit_2026.csv"
    sqlite_db_path: Path = PROJECT_ROOT / "data" / "export" / "draft_kit_2026.db"

    @property
    def export_dir(self) -> Path:
        return self.export_data_dir

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        for d in [self.data_dir, self.raw_data_dir, self.processed_data_dir, self.export_data_dir]:
            d.mkdir(parents=True, exist_ok=True)


@dataclass
class LeagueConfig:
    season: int = field(default_factory=lambda: int(os.getenv("LEAGUE_SEASON", os.getenv("SEASON", "2026"))))
    format: str = field(default_factory=lambda: os.getenv("SCORING_FORMAT", os.getenv("LEAGUE_FORMAT", "HALF_PPR")).upper())
    teams: int = field(default_factory=lambda: int(os.getenv("TOTAL_TEAMS", os.getenv("LEAGUE_TEAMS", "12"))))
    starters_qb: int = field(default_factory=lambda: int(os.getenv("ROSTER_QB", os.getenv("STARTERS_QB", "1"))))
    starters_rb: int = field(default_factory=lambda: int(os.getenv("ROSTER_RB", os.getenv("STARTERS_RB", "2"))))
    starters_wr: int = field(default_factory=lambda: int(os.getenv("ROSTER_WR", os.getenv("STARTERS_WR", "2"))))
    starters_te: int = field(default_factory=lambda: int(os.getenv("ROSTER_TE", os.getenv("STARTERS_TE", "1"))))
    starters_flex: int = field(default_factory=lambda: int(os.getenv("ROSTER_FLEX", os.getenv("STARTERS_FLEX", "1"))))
    starters_k: int = field(default_factory=lambda: int(os.getenv("ROSTER_K", os.getenv("STARTERS_K", "1"))))
    starters_dst: int = field(default_factory=lambda: int(os.getenv("ROSTER_DST", os.getenv("STARTERS_DST", "1"))))
    starters_superflex: int = field(default_factory=lambda: int(os.getenv("ROSTER_SUPERFLEX", os.getenv("STARTERS_SUPERFLEX", "0"))))
    bench_slots: int = field(default_factory=lambda: int(os.getenv("ROSTER_BENCH", os.getenv("BENCH_SLOTS", "5"))))

    replacement_qb_rank: int = field(default_factory=lambda: int(os.getenv("REPLACEMENT_QB_RANK", "12")))
    replacement_rb_rank: int = field(default_factory=lambda: int(os.getenv("REPLACEMENT_RB_RANK", "24")))
    replacement_wr_rank: int = field(default_factory=lambda: int(os.getenv("REPLACEMENT_WR_RANK", "24")))
    replacement_te_rank: int = field(default_factory=lambda: int(os.getenv("REPLACEMENT_TE_RANK", "12")))

    @property
    def total_starter_slots(self) -> int:
        return (
            self.starters_qb
            + self.starters_rb
            + self.starters_wr
            + self.starters_te
            + self.starters_flex
            + self.starters_k
            + self.starters_dst
            + self.starters_superflex
        )

    @property
    def total_roster_slots(self) -> int:
        return self.total_starter_slots + self.bench_slots

    @property
    def roster_display_string(self) -> str:
        parts = [
            f"{self.starters_qb}QB",
            f"{self.starters_rb}RB",
            f"{self.starters_wr}WR",
            f"{self.starters_te}TE",
            f"{self.starters_flex}FLEX",
        ]
        if self.starters_superflex > 0:
            parts.append(f"{self.starters_superflex}SF")
        if self.starters_k > 0:
            parts.append(f"{self.starters_k}K")
        if self.starters_dst > 0:
            parts.append(f"{self.starters_dst}DEF")
        return f"{' / '.join(parts)} ({self.bench_slots} Bench Slots)"

    def get_replacement_cutoff(self, position: str) -> int:
        pos = position.upper()
        if pos == "QB":
            return self.replacement_qb_rank or (self.teams * self.starters_qb)
        elif pos == "RB":
            return self.replacement_rb_rank or (self.teams * self.starters_rb)
        elif pos == "WR":
            return self.replacement_wr_rank or (self.teams * self.starters_wr)
        elif pos == "TE":
            return self.replacement_te_rank or (self.teams * self.starters_te)
        elif pos == "K":
            return self.teams * self.starters_k if self.starters_k > 0 else self.teams
        elif pos == "DST":
            return self.teams * self.starters_dst if self.starters_dst > 0 else self.teams
        return 12


@dataclass
class ModelWeights:
    weight_adj_ppg: float = field(default_factory=lambda: float(os.getenv("WEIGHT_ADJ_PPG", "0.30")))
    weight_luck_regression: float = field(default_factory=lambda: float(os.getenv("WEIGHT_LUCK_REGRESSION", "0.25")))
    weight_env_multiplier: float = field(default_factory=lambda: float(os.getenv("WEIGHT_ENV_MULTIPLIER", "0.25")))
    weight_steam_index: float = field(default_factory=lambda: float(os.getenv("WEIGHT_STEAM_INDEX", "0.20")))


@dataclass
class Settings:
    credentials: ApiCredentials = field(default_factory=ApiCredentials)
    paths: PathConfig = field(default_factory=PathConfig)
    league: LeagueConfig = field(default_factory=LeagueConfig)
    weights: ModelWeights = field(default_factory=ModelWeights)

    def __post_init__(self):
        self.paths.ensure_directories()


# Global settings singleton
settings = Settings()
