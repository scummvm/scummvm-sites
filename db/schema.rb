# encoding: UTF-8
# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your
# database schema. If you need to create the application database on another
# system, you should be using db:schema:load, not running all the migrations
# from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema.define(version: 20160609004409) do

  create_table "activities", force: :cascade do |t|
    t.integer  "trackable_id"
    t.string   "trackable_type"
    t.integer  "owner_id"
    t.string   "owner_type"
    t.string   "key"
    t.text     "parameters"
    t.integer  "recipient_id"
    t.string   "recipient_type"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "activities", ["owner_id", "owner_type"], name: "index_activities_on_owner_id_and_owner_type"
  add_index "activities", ["recipient_id", "recipient_type"], name: "index_activities_on_recipient_id_and_recipient_type"
  add_index "activities", ["trackable_id", "trackable_type"], name: "index_activities_on_trackable_id_and_trackable_type"

  create_table "engines", force: :cascade do |t|
    t.string   "name"
    t.string   "code"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "friendly_id_slugs", force: :cascade do |t|
    t.string   "slug",                      null: false
    t.integer  "sluggable_id",              null: false
    t.string   "sluggable_type", limit: 50
    t.string   "scope"
    t.datetime "created_at"
  end

  add_index "friendly_id_slugs", ["slug", "sluggable_type", "scope"], name: "index_friendly_id_slugs_on_slug_and_sluggable_type_and_scope", unique: true
  add_index "friendly_id_slugs", ["slug", "sluggable_type"], name: "index_friendly_id_slugs_on_slug_and_sluggable_type"
  add_index "friendly_id_slugs", ["sluggable_id"], name: "index_friendly_id_slugs_on_sluggable_id"
  add_index "friendly_id_slugs", ["sluggable_type"], name: "index_friendly_id_slugs_on_sluggable_type"

  create_table "games", force: :cascade do |t|
    t.string   "name"
    t.string   "developer"
    t.datetime "created_at",              null: false
    t.datetime "updated_at",              null: false
    t.integer  "engine_id"
    t.string   "slug"
    t.string   "box_art"
    t.integer  "first_release"
    t.integer  "introductory_release_id"
  end

  add_index "games", ["slug"], name: "index_games_on_slug", unique: true

  create_table "languages", force: :cascade do |t|
    t.string   "label"
    t.string   "code"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "platforms", force: :cascade do |t|
    t.string   "name"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string   "slug"
  end

  add_index "platforms", ["slug"], name: "index_platforms_on_slug", unique: true

  create_table "releases", force: :cascade do |t|
    t.integer  "major"
    t.integer  "minor"
    t.integer  "patch"
    t.date     "release_date"
    t.datetime "created_at",   null: false
    t.datetime "updated_at",   null: false
    t.string   "notes"
  end

  create_table "tests", force: :cascade do |t|
    t.integer  "version_id"
    t.integer  "user_id"
    t.integer  "compatibility"
    t.string   "user_system"
    t.integer  "release_id"
    t.string   "release_notes"
    t.string   "comment"
    t.datetime "created_at",    null: false
    t.datetime "updated_at",    null: false
    t.integer  "game_id"
  end

  add_index "tests", ["release_id"], name: "index_tests_on_release_id"
  add_index "tests", ["user_id"], name: "index_tests_on_user_id"
  add_index "tests", ["version_id"], name: "index_tests_on_version_id"

  create_table "users", force: :cascade do |t|
    t.string   "username",               default: "", null: false
    t.string   "email",                  default: "", null: false
    t.datetime "created_at",                          null: false
    t.datetime "updated_at",                          null: false
    t.string   "encrypted_password",     default: "", null: false
    t.string   "reset_password_token"
    t.datetime "reset_password_sent_at"
    t.datetime "remember_created_at"
    t.integer  "sign_in_count",          default: 0,  null: false
    t.datetime "current_sign_in_at"
    t.datetime "last_sign_in_at"
    t.string   "current_sign_in_ip"
    t.string   "last_sign_in_ip"
    t.string   "confirmation_token"
    t.datetime "confirmed_at"
    t.datetime "confirmation_sent_at"
    t.string   "unconfirmed_email"
    t.integer  "failed_attempts",        default: 0,  null: false
    t.string   "unlock_token"
    t.datetime "locked_at"
  end

  add_index "users", ["email"], name: "index_users_on_email", unique: true
  add_index "users", ["reset_password_token"], name: "index_users_on_reset_password_token", unique: true

  create_table "versions", force: :cascade do |t|
    t.integer  "platform_id"
    t.integer  "game_id"
    t.date     "release_date"
    t.string   "aliases"
    t.integer  "introductory_release_id"
    t.datetime "created_at",              null: false
    t.datetime "updated_at",              null: false
    t.integer  "language_id"
  end

end
