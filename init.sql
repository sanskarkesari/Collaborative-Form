CREATE TABLE forms (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    share_token UUID NOT NULL UNIQUE
);

CREATE TABLE fields (
    id UUID PRIMARY KEY,
    form_id UUID NOT NULL,
    type VARCHAR(50) NOT NULL,
    label VARCHAR(255) NOT NULL,
    options JSONB,
    "order" INT NOT NULL,
    required BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (form_id) REFERENCES forms(id) ON DELETE CASCADE
);

CREATE TABLE responses (
    id UUID PRIMARY KEY,
    form_id UUID NOT NULL,
    data JSONB NOT NULL,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (form_id) REFERENCES forms(id) ON DELETE CASCADE
);

CREATE INDEX idx_responses_form_id ON responses (form_id);