class CreateLanguages < ActiveRecord::Migration
  def change
    create_table :languages do |t|
      t.string :label
      t.string :code

      t.timestamps null: false
    end
  end
end
