class EnginesController < ApplicationController
  before_action :set_engine, only: [:show, :edit, :update, :destroy]

  # GET /engines
  # GET /engines.json
  def index
    @engines = Engine.all
  end

  # GET /engines/1
  # GET /engines/1.json
  def show
  end

  # GET /engines/new
  def new
    @engine = Engine.new
  end

  # GET /engines/1/edit
  def edit
  end

  # POST /engines
  # POST /engines.json
  def create
    @engine = Engine.new(engine_params)

    respond_to do |format|
      if @engine.save
        format.html { redirect_to @engine, notice: 'Engine was successfully created.' }
        format.json { render :show, status: :created, location: @engine }
      else
        format.html { render :new }
        format.json { render json: @engine.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /engines/1
  # PATCH/PUT /engines/1.json
  def update
    respond_to do |format|
      if @engine.update(engine_params)
        format.html { redirect_to @engine, notice: 'Engine was successfully updated.' }
        format.json { render :show, status: :ok, location: @engine }
      else
        format.html { render :edit }
        format.json { render json: @engine.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /engines/1
  # DELETE /engines/1.json
  def destroy
    @engine.destroy
    respond_to do |format|
      format.html { redirect_to engines_url, notice: 'Engine was successfully destroyed.' }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_engine
      @engine = Engine.find(params[:id])
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def engine_params
      params.require(:engine).permit(:name, :code)
    end
end
