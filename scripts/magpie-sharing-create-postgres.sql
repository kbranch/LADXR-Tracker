--
-- PostgreSQL database dump
--

-- Dumped from database version 13.3 (Debian 13.3-1.pgdg100+1)
-- Dumped by pg_dump version 14.11 (Ubuntu 14.11-0ubuntu0.22.04.1)

-- Started on 2024-05-16 18:55:24 EDT

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 206 (class 1255 OID 17997)
-- Name: purge_stale(); Type: PROCEDURE; Schema: public; Owner: -
--

CREATE PROCEDURE public.purge_stale()
    LANGUAGE sql
    AS $$delete from sharing
using settings
where settings.name = 'stalePlayerHours'
      and sharing.creation_time < (current_timestamp - interval '1 hour' * settings.value::integer);

delete from events
using settings
where settings.name = 'staleEventHours'
      and events.last_activity < (current_timestamp - interval '1 hour' * settings.value::integer);$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 203 (class 1259 OID 17976)
-- Name: events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.events (
    event_id bigint NOT NULL,
    name character varying(80) NOT NULL,
    join_code character varying(80),
    view_code character varying(80),
    creation_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_activity timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- TOC entry 202 (class 1259 OID 17974)
-- Name: events_event_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.events_event_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2965 (class 0 OID 0)
-- Dependencies: 202
-- Name: events_event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.events_event_id_seq OWNED BY public.events.event_id;


--
-- TOC entry 205 (class 1259 OID 17988)
-- Name: settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.settings (
    setting_id bigint NOT NULL,
    name character varying(80) NOT NULL,
    value character varying(80)
);


--
-- TOC entry 204 (class 1259 OID 17986)
-- Name: settings_setting_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.settings_setting_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2966 (class 0 OID 0)
-- Dependencies: 204
-- Name: settings_setting_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.settings_setting_id_seq OWNED BY public.settings.setting_id;


--
-- TOC entry 201 (class 1259 OID 16774)
-- Name: sharing; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sharing (
    sharing_id bigint NOT NULL,
    player_name character varying(80) NOT NULL,
    player_id uuid NOT NULL,
    event_name character varying(80),
    state text NOT NULL,
    "timestamp" numeric(23,3) NOT NULL,
    player_no integer,
    creation_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- TOC entry 200 (class 1259 OID 16772)
-- Name: sharing_sharingId_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."sharing_sharingId_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2967 (class 0 OID 0)
-- Dependencies: 200
-- Name: sharing_sharingId_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."sharing_sharingId_seq" OWNED BY public.sharing.sharing_id;


CREATE TABLE public.location_sharing
(
    location_sharing_id bigserial NOT NULL,
    player_name character varying(80) NOT NULL,
    session_id uuid NOT NULL,
    room character varying(10) NOT NULL,
    x integer NOT NULL,
    y integer NOT NULL,
    "timestamp" numeric(23, 3) NOT NULL,
    creation_time timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (location_sharing_id)
);

ALTER TABLE IF EXISTS public.location_sharing
    OWNER to postgres;

CREATE TABLE public.tips
(
    tip_id bigserial NOT NULL,
    connection_id character varying(100) NOT NULL,
    body character varying(10000) NOT NULL,
    attribution character varying(200) NOT NULL,
    language character varying(10) NOT NULL,
    approved boolean NOT NULL DEFAULT FALSE,
    show boolean NOT NULL DEFAULT TRUE,
    creation_time timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tip_id)
);

CREATE TABLE public.tip_attachments
(
    tip_attachment_id bigserial NOT NULL,
    tip_id bigint NOT NULL,
    filename character varying(255) NOT NULL,
    show boolean NOT NULL DEFAULT TRUE,
    creation_time timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tip_attachment_id),
    CONSTRAINT tip_attachment_tip_id_fk FOREIGN KEY (tip_id)
        REFERENCES public.tips (tip_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

--
-- TOC entry 2819 (class 2604 OID 17979)
-- Name: events event_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.events ALTER COLUMN event_id SET DEFAULT nextval('public.events_event_id_seq'::regclass);


--
-- TOC entry 2822 (class 2604 OID 17991)
-- Name: settings setting_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.settings ALTER COLUMN setting_id SET DEFAULT nextval('public.settings_setting_id_seq'::regclass);


--
-- TOC entry 2817 (class 2604 OID 16777)
-- Name: sharing sharing_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sharing ALTER COLUMN sharing_id SET DEFAULT nextval('public."sharing_sharingId_seq"'::regclass);


--
-- TOC entry 2826 (class 2606 OID 17982)
-- Name: events events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (event_id);


--
-- TOC entry 2828 (class 2606 OID 17993)
-- Name: settings settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT settings_pkey PRIMARY KEY (setting_id);


--
-- TOC entry 2824 (class 2606 OID 16782)
-- Name: sharing sharing_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sharing
    ADD CONSTRAINT sharing_pkey PRIMARY KEY (sharing_id);


--
-- TOC entry 2964 (class 0 OID 0)
-- Dependencies: 206
-- Name: PROCEDURE purge_stale(); Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON PROCEDURE public.purge_stale() TO postgres;


-- Completed on 2024-05-16 18:55:24 EDT

--
-- PostgreSQL database dump complete
--

